
#创建猫眼movie表01 爬虫启动前先执行此sql
CREATE TABLE `movie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `movie_url` varchar(255) DEFAULT NULL,
  `movie_name` varchar(255) DEFAULT NULL,
  `ename` varchar(255) DEFAULT NULL,
  `movie_desc` text,
  `infos` varchar(255) DEFAULT NULL,
  `celebritys` varchar(255) DEFAULT NULL,
  `actors` text,
  `req_url` varchar(255) DEFAULT NULL,
  movie_type varchar(255) DEFAULT NULL,
  movie_area varchar(255) DEFAULT NULL,
  movie_minutes varchar(255) DEFAULT NULL,
  movie_year varchar(255) DEFAULT NULL,
  movie_time varchar(255) DEFAULT NULL,
  player_type varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

#数据处理sql脚本02 数据处理首先执行
update movie 
set movie_type=substring_index(infos,";",1)
,movie_area=substring_index(substring_index(substring_index(infos,";",2),";",-1),"/",1)
,movie_minutes=case when instr(infos,'/')>0 then replace(substring_index(substring_index(substring_index(infos,";",2),";",-1),"/",-1),'分钟','') else null end
,movie_year=case when instr(substring_index(infos,";",-1),'映')>0 then left(substring_index(infos,";",-1),4) else null end
,movie_time=case when instr(substring_index(infos,";",-1),'映')>0 then replace(substring_index(infos,";",-1),right(infos,4),'')
when instr(substring_index(infos,";",-1),'映')>0 and instr(substring_index(infos,";",-1),'-')=0 then concat(replace(substring_index(infos,";",-1),right(infos,4),''),"-01-01")
else null end 
,player_type=right(infos,4) ;

##数据处理sql脚本03 数据处理再次执行

update movie set movie_time=
case when length(movie_time)=10 then movie_time
when length(movie_time)=4 then concat(movie_time,"-01-01") 
when length(movie_time)=7 then concat(movie_time,"-01") 
when length(movie_time)>4 and length(substring_index(movie_time,"-",-1))=1 then concat(movie_year,"-0",substring_index(movie_time,"-",-1),"-01")
else null end
