Python Files Description:
==========================================================

==========================================================




DESCRIPTION OF THE DATABASE
==========================================================
The Database Name is: popsfundamental

\c popsfundamental

==========================================================
Table I: df_games_2013

popsfundamental=# select count(*) from information_schema.columns where table_name='df_games_2013';
 count 
-------
   253
(1 row)

popsfundamental=# select count(*) from df_games_2013;
 count 
-------
  2458
(1 row)

popsfundamental=# \d+ df_games;
                             Table "public.df_games"
        Column         | Type | Modifiers | Storage  | Stats target | Description 
-----------------------+------+-----------+----------+--------------+-------------
 reserve_f_stl_per     | text |           | extended |              | 
 starters_blk          | text |           | extended |              | 
 reserves_drb_per      | text |           | extended |              | 
 reserve_f_blk_per     | text |           | extended |              | 
 team_ft_per           | text |           | extended |              | 
 reserve_g_fga         | text |           | extended |              | 
 team_trb              | text |           | extended |              | 
 reserve_g_tov         | text |           | extended |              | 
 team_3pa              | text |           | extended |              | 
 team_fg_per           | text |           | extended |              | 
 reserve_f_ast         | text |           | extended |              | 
 starters_drb          | text |           | extended |              | 
 starting_g_ast        | text |           | extended |              | 
 team_ast              | text |           | extended |              | 
 reserves_blk          | text |           | extended |              | 
 team_stl_per          | text |           | extended |              | 
 reserves_trb_per      | text |           | extended |              | 
 reserves_pf           | text |           | extended |              | 
...It has been cut off.
