-- CREATE DATABASE cafe
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;

BEGIN;


CREATE TABLE IF NOT EXISTS public.roles
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    role text,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.users
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    email text NOT NULL,
    password text NOT NULL,
    lastname text NOT NULL,
    firstname text NOT NULL,
    password_changed boolean NOT NULL,
    status boolean NOT NULL DEFAULT true,
    last_activity timestamp without time zone,
    role integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.history
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "user" bigint NOT NULL,
    action text NOT NULL,
    "time" timestamp without time zone NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.menu
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    name text NOT NULL,
    description text,
    rate text,
    price real,
    category integer,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.orders
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "user" bigint NOT NULL,
    "time" timestamp without time zone NOT NULL,
    summa real NOT NULL,
    "table" integer,
    status integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.comments
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "user" bigint NOT NULL,
    food bigint NOT NULL,
    comment text NOT NULL,
    "time" timestamp without time zone NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.order_list
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "order" bigint NOT NULL,
    food bigint NOT NULL,
    count integer NOT NULL,
    summ real NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.order_status
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    status text,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.cart
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "user" bigint NOT NULL,
    food bigint NOT NULL,
    count integer NOT NULL,
    summ real NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.category
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    name text NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.users
    ADD CONSTRAINT role FOREIGN KEY (role)
    REFERENCES public.roles (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.history
    ADD CONSTRAINT "user" FOREIGN KEY ("user")
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.menu
    ADD FOREIGN KEY (category)
    REFERENCES public.category (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.orders
    ADD CONSTRAINT "user" FOREIGN KEY ("user")
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.orders
    ADD CONSTRAINT status FOREIGN KEY (status)
    REFERENCES public.order_status (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.comments
    ADD CONSTRAINT food FOREIGN KEY (food)
    REFERENCES public.menu (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.comments
    ADD CONSTRAINT "user" FOREIGN KEY ("user")
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.order_list
    ADD CONSTRAINT "order" FOREIGN KEY ("order")
    REFERENCES public.orders (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.order_list
    ADD CONSTRAINT food FOREIGN KEY (food)
    REFERENCES public.menu (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.cart
    ADD CONSTRAINT "user" FOREIGN KEY ("user")
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.cart
    ADD CONSTRAINT food FOREIGN KEY (food)
    REFERENCES public.menu (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

END;

-- Insert roles
INSERT INTO public.roles (role) VALUES
('admin'),
('customer'),
('staff');


-- Insert order statuses
INSERT INTO public.order_status (status) VALUES
('Pending'),
('Confirmed'),
('Completed'),
('Cancelled');

INSERT INTO public.category (name) VALUES ('Горячие блюда'), ('Соки'), ('Закуски') returning id;

-- Insert menu items with fish
INSERT INTO public.menu (name, description, rate, price, category) VALUES
('Grilled Salmon', 'Свежий филе лосося, приготовленное до идеального состояния', '4.6', 12.99, 1),
('Fish and Chips', 'Классическое блюдо из рыбы в кляре подаётся с картофелем фри', '4.4', 9.99, 1),
('Fish Tacos', 'Мягкие тортильи с хрустящей рыбой, сальсой и капустным салатом', '4.3', 8.99, 1),
('Fish Curry', 'Ароматное карри с нежными кусочками рыбы и душистыми специями', '4.5', 11.99, 1),
('Seafood Pasta', 'Паста в сливочном соусе с креветками, морскими гребешками и рыбой', '4.7', 14.99, 1);
