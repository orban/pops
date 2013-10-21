TYPE I: PLAYERS
========================================
1. players_bbref

popsfundamental=# \d players_bbref 
   Table "public.players_bbref"
    Column     | Type | Modifiers 
---------------+------+-----------
 player_bbr_id | text | 
 player        | text | 
 pos           | text | 
 first         | text | 
 last          | text | 
 ht            | text | 
 wt            | text | 
 birth         | text | 
 college       | text | 
 link          | text | 

popsfundamental=# select count(*) from players_bbref;
 count 
-------
  4139

TYPE II: GAMES
======================
1. results_id_links_2013

popsfundamental=# \d results_id_links_2013
      Table "public.results_id_links_2013"
   Column    |         Type          | Modifiers 
-------------+-----------------------+-----------
 game_id     | smallint              | not null
 game        | character varying(30) | not null
 date        | date                  | not null
 home        | character varying(25) | not null
 pts_home    | smallint              | not null
 visitor     | character varying(25) | not null
 pts_visitor | smallint              | not null
 ot          | character varying(5)  | not null
 link        | character varying(50) | not null

game_id |        game        |    date    |        home        | pts_home |       visitor       | pts_visitor | ot |             link             
---------+--------------------+------------+--------------------+----------+---------------------+-------------+----+------------------------------
       1 | 2012-10-30_WAS_CLE | 2012-10-30 | Washington Wizards |       84 | Cleveland Cavaliers |          94 | -  | /boxscores/201210300CLE.html


TYPE III: SEASONS
======================
1. result_atl_2013

popsfundamental=# select * from result_atl_2013 limit 5;
 g |    date    | home |          opp          | result | ot | score_t | score_o | w | l | streak 
---+------------+------+-----------------------+--------+----+---------+---------+---+---+--------
 1 | 2012-11-02 |    1 | Houston Rockets       | L      | -  |     102 |     109 | 0 | 1 |     -1

popsfundamental=# select count(*) from result_atl_2013 ;
 count 
-------
    82

And there are 30 of such tables:
 public | result_atl_2013       | table | jhuang
 public | result_bos_2013       | table | jhuang
 public | result_cha_2013       | table | jhuang
 public | result_chi_2013       | table | jhuang
 public | result_cle_2013       | table | jhuang
 public | result_dal_2013       | table | jhuang
 public | result_den_2013       | table | jhuang
 public | result_det_2013       | table | jhuang
 public | result_gsw_2013       | table | jhuang
 public | result_hou_2013       | table | jhuang
 public | result_ind_2013       | table | jhuang
 public | result_lac_2013       | table | jhuang
 public | result_lal_2013       | table | jhuang
 public | result_mem_2013       | table | jhuang
 public | result_mia_2013       | table | jhuang
 public | result_mil_2013       | table | jhuang
 public | result_min_2013       | table | jhuang
 public | result_njn_2013       | table | jhuang
 public | result_noh_2013       | table | jhuang
 public | result_nyk_2013       | table | jhuang
 public | result_okc_2013       | table | jhuang
 public | result_orl_2013       | table | jhuang
 public | result_phi_2013       | table | jhuang
 public | result_pho_2013       | table | jhuang
 public | result_por_2013       | table | jhuang
 public | result_sac_2013       | table | jhuang
 public | result_sas_2013       | table | jhuang
 public | result_tor_2013       | table | jhuang
 public | result_uta_2013       | table | jhuang
 public | result_was_2013       | table | jhuang
