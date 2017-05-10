import MySQLdb as mdb
import numbers
import json
import config_scrapy as config

con = mdb.connect(config.db_host, config.db_user, config.db_pwd, config.db_database);
match_keywords = {
    'double':'double-stroller',
    'stroller':'strollers',
    'inline':'inline-stroller',
    'travel system':'travel-system',
    'jog':'jogger',
    'car seat':'carseat',
    'carrier':'carriers',
    'activity center':'activity-center',
    'furniture':'baby-furniture',
    'changer':'changers',
    'bassinet':'bassinets',
    'bumper':'bumpers',
    'soother':'soothers',
    'high chair':'highchair',
    'food processor':'food-processor',
    'bath tub':'bathtub',
    'warmer':'wamer',
    'puree':'puree-blender',
    'blender':'blender-juicer',
    'proof':'proof-devices',
    'gate':'gates',
    'monitor':'monitors',
    'rail':'bed-rails',
    'book':'books',
    'walker':'walkers',
    'stacker':'stackers',
    'juicer':'blender-juicer',
    'tandem':'tandem-stroller',
    'potty':'bathpotty',

    'diaper bag':'diper-bag',
    'swings':'swing',
    'convertible':'',
    'crib':'standard-crib',
}

def retrieve_data(sql):
    with con:
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

def insert_many(sql, sqldata):
    with con:
        cur = con.cursor()
        cur.executemany(sql, sqldata)
        con.commit()

def execute_sql(sql):
    with con:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

def delete_posts():
    sql  = "DELETE FROM wp_posts WHERE ID > 4000000000"
    execute_sql(sql)

    sql  = "DELETE FROM wp_postmeta WHERE post_id > 4000000000"
    execute_sql(sql)

    sql  = "DELETE FROM wp_term_relationships WHERE object_id > 4000000000"
    execute_sql(sql)

def insert_posts(item_list):
    post_sql = """INSERT INTO wp_posts (ID, post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt,\
         post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified,\
         post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count) \
         VALUES (
            %s,
            %s,
            Now(),
            Now(),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            Now(),
            Now(),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s)"""

    terms_sql = "INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)"
    meta_sql = "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s) "

    post_data_list = []
    image_post_data_list = []
    terms_data_list = []
    meta_data_list = []

    for i in range(len(item_list)):
        item = item_list[i]
        #Image Post Part

        image_ind = 0
        image_meta_id = []
        for row in item.image:
            original_file_name = ""
            thumb_file_name = ""

            if row["original"] is not None:
                original_file_name =  row["original"].rsplit("/",1)[1]

            try:
                thumb_file_name =  row["thumb"].rsplit("/",1)[1]

            except KeyError:
                thumb_file_name = ""

            image_ind += 1
            image_id = int('900' + str(image_ind) + item.post_id)
            image_meta_id.append(str(image_id))

            try:
                file_path = "files/" + item.post_id + "/" + original_file_name
                image_post_data = (
                    image_id,              #ID
                    1,                             #post_author
                    # now(),                       #post_date
                    # now(),                       #post_date_gmt
                    "",                             #post_content
                    item.post_id,                     #post_title
                    "",                            #post_excerpt
                    "inherit",                      #post_status
                    "open",                            #comment_status
                    "closed",                            #ping_status
                    "",                            #post_password
                    item.post_id,                      #post_name
                    "",                            #to_ping
                    "",                            #pinged
                    # now(),                            #post_modified
                    # now(),                            #post_modified_gmt
                    "",                            #post_content_filtered
                    0,                            #post_parent
                    config.root_path + "wp-content/uploads/" + file_path,       #guid
                    0,                            #menu_order
                    "attachment",                            #post_type
                    "image/jpeg",                            #post_mime_type
                    1)                            #comment_count
            except:
                print row
                print item
                return

            meta_data = (image_id, '_wp_attached_file', file_path)
            meta_data_list.append(meta_data)

            attach_meta_str = 'a:5:{s:5:"width";   i:450; s:6:"height";  i:600; s:4:"file";    s:28:"' + file_path + '"; s:5:"sizes";   a:9:{';
            if thumb_file_name != "":
                attach_meta_str +='s:9:"thumbnail";  a:4:{s:4:"file";s:28:"' + thumb_file_name + '"; s:5:"width";i:50;  s:6:"height";  i:50;  s:9:"mime-type";s:10:"image/jpeg";   }'
                attach_meta_str +='s:6:"medium"; a:4:{s:4:"file";s:28:"' + thumb_file_name +'";s:5:"width";i:50;  s:6:"height";  i:50;  s:9:"mime-type";s:10:"image/jpeg";   }'

            attach_meta_str +='s:12:"medium_large";  a:4:{ s:4:"file";  s:28:"' + original_file_name +'";    s:5:"width"; i:450;   s:6:"height";    i:600;   s:9:"mime-type";'
            attach_meta_str +='s:10:"image/jpeg";}s:23:"listable-carousel-image";   a:4:{ s:4:"file";  s:29:"' + original_file_name +'; s:5:"width"; i:450;   s:6:"height";'
            attach_meta_str +='i:600;   s:9:"mime-type"; s:10:"image/jpeg"; } } s:10:"image_meta"; a:12:{ s:8:"aperture";   s:1:"0";  s:6:"credit"; s:0:"";   s:6:"camera"; s:0:"";'
            attach_meta_str +='s:7:"caption";    s:0:"";   s:17:"created_timestamp"; s:1:"0";  s:9:"copyright";  s:0:"";   s:12:"focal_length";  s:1:"0";  s:3:"iso";'
            attach_meta_str +='s:1:"0";  s:13:"shutter_speed"; s:1:"0";  s:5:"title";  s:0:"";   s:11:"orientation";   s:1:"0";  s:8:"keywords";   a:0:{ }  }'

            meta_data = (image_id, '_wp_attachment_metadata', attach_meta_str)
            meta_data_list.append(meta_data)

            image_post_data_list.append(image_post_data)

        #Product Post Part
        post_data = (
            int(item.post_id),              #ID
            1,                             #post_author
            # now(),                       #post_date
            # now(),                       #post_date_gmt
            item.description,   #post_content
            item.product_name,                            #post_title
            "",                            #post_excerpt
            "publish",                            #post_status
            "open",                            #comment_status
            "open",                            #ping_status
            "",                            #post_password
            item.post_id,                #post_name
            "",                            #to_ping
            "",                            #pinged
            # now(),                            #post_modified
            # now(),                            #post_modified_gmt
            "",                            #post_content_filtered
            0,                            #post_parent
            config.root_path + "listings/" + item.post_id,     #guid
            0,                            #menu_order
            "job_listing",                            #post_type
            "",                            #post_mime_type
            0)                            #comment_count

        post_data_list.append(post_data);

        #Product Post Meta Part
        meta_data = (int(item.post_id), 'geolocation_lat', str(item.latitude))
        meta_data_list.append(meta_data)

        meta_data = (int(item.post_id), 'geolocation_long', str(item.longitude))
        meta_data_list.append(meta_data)

        if len(image_meta_id) > 0:
            meta_data = (int(item.post_id), 'main_image', ",".join(image_meta_id))
            meta_data_list.append(meta_data)

        #Product Terms Relations(Category) Part
        if isinstance(item.keyword, numbers.Integral) == True:
            terms_data = (int(item.post_id), item.keyword, 0)
            terms_data_list.append(terms_data)

    insert_many(post_sql, post_data_list)
    insert_many(post_sql, image_post_data_list)
    insert_many(meta_sql, meta_data_list)
    insert_many(terms_sql, terms_data_list)

def get_product_info(id):
    product_info =  retrieve_data("select * from wp_posts where ID=" + id)
    return product_info

def get_product_list_from_db():
    product_lists =  retrieve_data("select * from wp_posts")
    return product_lists

def insert_data(item_list):
    keyword_rows = retrieve_data("select * from wp_terms")
    lost_keywords = []

    for row  in item_list:
        try:
            if match_keywords[row.keyword] != "":
                row.keyword = match_keywords[row.keyword]
        except:
            exists = 0

        for k_row in keyword_rows:
            if k_row[2] == row.keyword:
                row.keyword = k_row[0]

    insert_posts(item_list)
