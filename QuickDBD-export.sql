-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "User" (
    "id" int   NOT NULL,
    "Username" string   NOT NULL,
    "Showcount" int   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Searchlist" (
    "id" int   NOT NULL,
    "title" string   NOT NULL,
    "genre" string   NOT NULL,
    "episodes" int   NOT NULL,
    "avgRating" int   NOT NULL,
    "addshow" button   NOT NULL,
    CONSTRAINT "pk_Searchlist" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Userlist" (
    "id" int   NOT NULL,
    "user_id" INTEGER   NOT NULL,
    "anime_id" INTEGER   NOT NULL,
    CONSTRAINT "pk_Userlist" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "Userlist" ADD CONSTRAINT "fk_Userlist_user_id" FOREIGN KEY("user_id")
REFERENCES "User" ("id");

ALTER TABLE "Userlist" ADD CONSTRAINT "fk_Userlist_anime_id" FOREIGN KEY("anime_id")
REFERENCES "Searchlist" ("id");

