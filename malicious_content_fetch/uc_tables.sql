-- Database: UC

-- DROP DATABASE UC;

CREATE DATABASE UC
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
--------------------------------------
-- Table: public.malwares

-- DROP TABLE public.malwares;

CREATE TABLE IF NOT EXISTS public.malwares
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    first_seen_utc character varying(20) COLLATE pg_catalog."default",
    sha256_hash character varying(70) COLLATE pg_catalog."default",
    md5_hash character varying(35) COLLATE pg_catalog."default",
    sha1_hash character varying(45) COLLATE pg_catalog."default",
    reporter character varying(300) COLLATE pg_catalog."default",
    file_name character varying(300) COLLATE pg_catalog."default",
    file_type_guess character varying(200) COLLATE pg_catalog."default",
    mime_type character varying(300) COLLATE pg_catalog."default",
    signature character varying(300) COLLATE pg_catalog."default",
    clamav character varying(100) COLLATE pg_catalog."default",
    vtpercent character varying(100) COLLATE pg_catalog."default",
    imphash character varying(150) COLLATE pg_catalog."default",
    ssdeep character varying(150) COLLATE pg_catalog."default",
    tlsh character varying(150) COLLATE pg_catalog."default",
    last_seen_utc character varying(20) COLLATE pg_catalog."default",
    ip character varying(30) COLLATE pg_catalog."default",
    url character varying(300) COLLATE pg_catalog."default",
    size integer,
    confidence_level integer,
    tags character varying COLLATE pg_catalog."default",
    resource_name character varying(100) COLLATE pg_catalog."default",
    maintype character varying(50) COLLATE pg_catalog."default",
    subtype character varying(50) COLLATE pg_catalog."default",
    user_name character varying(100) COLLATE pg_catalog."default",
    datetime timestamp(0) without time zone,
    CONSTRAINT malwares_pkey PRIMARY KEY (id),
    CONSTRAINT "unique" UNIQUE (md5_hash)
        INCLUDE(resource_name),
    CONSTRAINT unique1 UNIQUE (sha256_hash)
        INCLUDE(resource_name)
)

TABLESPACE pg_default;

ALTER TABLE public.malwares
    OWNER to postgres;
-- Index: malwares_ind_datetime

-- DROP INDEX public.malwares_ind_datetime;

CREATE INDEX malwares_ind_datetime
    ON public.malwares USING btree
    (datetime ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: malwares_ind_md5

-- DROP INDEX public.malwares_ind_md5;

CREATE INDEX malwares_ind_md5
    ON public.malwares USING hash
    (md5_hash COLLATE pg_catalog."default")
    TABLESPACE pg_default;
-- Index: malwares_ind_sha256

-- DROP INDEX public.malwares_ind_sha256;

CREATE INDEX malwares_ind_sha256
    ON public.malwares USING hash
    (sha256_hash COLLATE pg_catalog."default")
    TABLESPACE pg_default;
--------------------------------------
-- Table: public.resources

-- DROP TABLE public.resources;

CREATE TABLE IF NOT EXISTS public.resources
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name character varying(100) COLLATE pg_catalog."default",
    maintype character varying(50) COLLATE pg_catalog."default",
    subtype character varying(50) COLLATE pg_catalog."default",
    url character varying(150) COLLATE pg_catalog."default",
    api_url character varying(150) COLLATE pg_catalog."default",
    api_key character varying(100) COLLATE pg_catalog."default",
    api_limit integer,
    schedule boolean DEFAULT false,
    schedule_period integer,
    datetime timestamp without time zone,
    CONSTRAINT resource_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.resources
    OWNER to postgres;
-----------------------------------
DROP TABLE public.malips;

CREATE TABLE IF NOT EXISTS public.malips
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    first_seen_utc character varying(20) COLLATE pg_catalog."default",
    ip character varying(100) COLLATE pg_catalog."default",
    port integer NOT NULL DEFAULT 0,
    ip_status character varying(10) COLLATE pg_catalog."default",
    confidence_level integer,
    usagetype character varying(100) COLLATE pg_catalog."default",
    domainname character varying(300) COLLATE pg_catalog."default",
    hostname character varying(300) COLLATE pg_catalog."default",
    country character varying(50) COLLATE pg_catalog."default",
    ispublic boolean,
    lastreportedat character varying(20) COLLATE pg_catalog."default",
    resource_name character varying(100) COLLATE pg_catalog."default",
    maintype character varying(50) COLLATE pg_catalog."default",
    subtype character varying(50) COLLATE pg_catalog."default",
    user_name character varying(100) COLLATE pg_catalog."default",
    datetime timestamp(0) without time zone,
    CONSTRAINT malips_pkey PRIMARY KEY (id),
    CONSTRAINT malips_uniq1 UNIQUE (ip, resource_name)
)

TABLESPACE pg_default;

ALTER TABLE public.malips
    OWNER to postgres;
-- Index: malips_ind_datetime

-- DROP INDEX public.malips_ind_datetime;

CREATE INDEX malips_ind_datetime
    ON public.malips USING btree
    (datetime ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: malips_ind_ip

-- DROP INDEX public.malips_ind_ip;

CREATE INDEX malips_ind_ip
    ON public.malips USING hash
    (ip COLLATE pg_catalog."default")
    TABLESPACE pg_default;
-----------------------------------------
-- Table: public.maliocs

-- DROP TABLE public.maliocs;

CREATE TABLE IF NOT EXISTS public.maliocs
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    first_seen_utc character varying(20) COLLATE pg_catalog."default",
    ioctype character varying(50) COLLATE pg_catalog."default",
    iocvalue character varying COLLATE pg_catalog."default",
    iocstatus character varying(10) COLLATE pg_catalog."default",
    fk_malware character varying COLLATE pg_catalog."default",
    malware_alias character varying COLLATE pg_catalog."default",
    malware_printable character varying COLLATE pg_catalog."default",
    confidence_level integer,
    reference character varying COLLATE pg_catalog."default",
    tags character varying COLLATE pg_catalog."default",
    last_seen_utc character varying(20) COLLATE pg_catalog."default",
    resource_name character varying(100) COLLATE pg_catalog."default",
    maintype character varying(50) COLLATE pg_catalog."default",
    subtype character varying(50) COLLATE pg_catalog."default",
    user_name character varying(100) COLLATE pg_catalog."default",
    datetime timestamp(0) without time zone,
    CONSTRAINT maliocs_pkey PRIMARY KEY (id),
    CONSTRAINT maliocs_uniq1 UNIQUE (iocvalue, resource_name)
)

TABLESPACE pg_default;

ALTER TABLE public.maliocs
    OWNER to postgres;
-- Index: maliocs_ind_ioc

-- DROP INDEX public.maliocs_ind_ioc;

CREATE INDEX maliocs_ind_ioc
    ON public.maliocs USING hash
    (iocvalue COLLATE pg_catalog."default")
    TABLESPACE pg_default;
-----------------------------------
-- Table: public.logs

-- DROP TABLE public.logs;

CREATE TABLE IF NOT EXISTS public.logs
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    log character varying COLLATE pg_catalog."default",
    ip character varying(30) COLLATE pg_catalog."default",
    user_name character varying(100) COLLATE pg_catalog."default",
    datetime timestamp without time zone,
    CONSTRAINT logs_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.logs
    OWNER to postgres;
---------------------------
-- Table: public.mal_files

-- DROP TABLE public.mal_files;

CREATE TABLE IF NOT EXISTS public.mal_files
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    malwares_id bigint,
    file_name character varying COLLATE pg_catalog."default",
    file bytea,
    file_size integer,
    ip character varying COLLATE pg_catalog."default",
    username character varying COLLATE pg_catalog."default",
    datetime time without time zone,
    CONSTRAINT mal_files_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.mal_files
    OWNER to postgres;
-------------------------------
