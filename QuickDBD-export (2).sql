-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "User" (
    "id" int   NOT NULL,
    "Email" string   NOT NULL,
    "Username" string   NOT NULL,
    "image_url" string   NOT NULL,
    "hashedpassword" string   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Anime" (
    "id" int   NOT NULL,
    "title" string   NOT NULL,
    "genre" string   NOT NULL,
    "episodes" int   NOT NULL,
    "avgRating" int   NOT NULL,
    CONSTRAINT "pk_Anime" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Episode" (
    "id" int   NOT NULL,
    "title" string   NOT NULL,
    "anime_id" INTEGER   NOT NULL,
    "userlist_id" INTEGER   NOT NULL,
    CONSTRAINT "pk_Episode" PRIMARY KEY (
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

ALTER TABLE "Episode" ADD CONSTRAINT "fk_Episode_anime_id" FOREIGN KEY("anime_id")
REFERENCES "Anime" ("id");

ALTER TABLE "Episode" ADD CONSTRAINT "fk_Episode_userlist_id" FOREIGN KEY("userlist_id")
REFERENCES "Userlist" ("id");

ALTER TABLE "Userlist" ADD CONSTRAINT "fk_Userlist_user_id" FOREIGN KEY("user_id")
REFERENCES "User" ("id");

ALTER TABLE "Userlist" ADD CONSTRAINT "fk_Userlist_anime_id" FOREIGN KEY("anime_id")
REFERENCES "Anime" ("id");

