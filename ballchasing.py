import fire
import datetime
import os
import random
from tinydb import TinyDB, Query
import ballchasing_downloader as bd
from ballchasing_downloader import mapper

replay_out_folder = 'data/replays/'
replay_conv_folder = 'data/converted/'
ballchasing_data_folder  = 'data/ballchasing_info/'
ballchasing_db_file = os.path.join(ballchasing_data_folder, 
                                   'ballchasing.db.json')
ballchasing_last_update_file = os.path.join(ballchasing_data_folder,
                                            'ballchasing.last.txt')

class Ballchasing:

    def __init__(self):
        self._db = TinyDB(ballchasing_db_file)

    def __last_upload_date(self):
        if not os.path.isfile(ballchasing_last_update_file):
            return None
        else:
            with open(ballchasing_last_update_file) as f:
                return datetime.datetime.fromtimestamp(float(f.read()))

    def __update_last_upload_date(self, new_date: datetime.datetime):
        with open(ballchasing_last_update_file, 'w') as f:
            f.write(str(new_date.timestamp()))

    def update_db(self, max_inserts=1000):
        insert_count = 0
        last_date = self.__last_upload_date()
        ret = bd.retreive_infos()
        new_infos = [mapper.named_tuple_to_dict(mi) for mi in ret 
                     if ((last_date is None) or (mi.upload_date > last_date))]
        self._db.insert_multiple(new_infos)
        insert_count += len(new_infos)
        last_id = ret[-1].id
        new_last_date = max([mi.upload_date for mi in ret])

        while (len(new_infos) > 0 and 
               (insert_count < max_inserts or max_inserts is 0)):
            try:
                ret = bd.retreive_infos(last_id)
                if len(ret) == 0:
                    break
            except Exception as e:
                print('Error while parsing infos after id={}'.format(last_id))
                print('A total of {} infos where retreived'.format(insert_count))
                raise

            new_infos = [mapper.named_tuple_to_dict(mi) for mi in ret 
                         if ((last_date is None) 
                             or (mi.upload_date > last_date))]
            self._db.insert_multiple(new_infos)
            insert_count += len(new_infos)
            last_id = ret[-1].id

        self.__update_last_upload_date(new_last_date)
        print('Inserted {} new match infos'.format(insert_count))

    def clean_db(self):
        os.remove(ballchasing_db_file)
        os.remove(ballchasing_last_update_file)


    def download_replays(self):
        missing_ids = bd.filter_downloaded_ids(replay_out_folder, ballchasing_db_file)
        for id in missing_ids:
            bd.download_replay(id, replay_out_folder)


    def convert_replays(self, number=10):
        'Converts {number} random replays into its dataframe and game info'
        to_convert_ids = bd.filter_converted_ids(replay_out_folder, 
                                                 replay_conv_folder)
        if number > 0:
            to_convert_ids = random.sample(to_convert_ids, k=number)

        with open('converting_errors.log', 'a') as f:
            for id in to_convert_ids:
                try:
                    bd.convert_replay(
                        os.path.join(replay_out_folder, id + '.replay'),
                        replay_conv_folder)
                except Exception as e:
                    print(ValueError(
                        'Could not convert replay with id {}'.format(id), e),
                        file=f
                    )


if __name__ == '__main__':
    fire.Fire(Ballchasing)
