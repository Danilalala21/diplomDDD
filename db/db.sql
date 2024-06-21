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
    photo text,
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


INSERT INTO public.category (name) VALUES
('Горячие блюда'),
('Соки'),
('Закуски'),
('Салаты'),
('Десерты'),
('Напитки');

INSERT INTO public.menu (name, description, rate, price, category, photo) VALUES
('Жареный лосось', 'Свежий филе лосося, приготовленное до идеального состояния', '4.6', 12.99, 1, 'losos.jpg'),
('Рыба и картофель', 'Классическое блюдо из рыбы в кляре подаётся с картофелем фри', '4.4', 9.99, 1, 'sudak.jpg'),
('Рыбные тако', 'Мягкие тортильи с хрустящей рыбой, сальсой и капустным салатом', '4.3', 8.99, 1, 'forel.jpg'),
('Рыбное карри', 'Ароматное карри с нежными кусочками рыбы и душистыми специями', '4.5', 11.99, 1, '30.jpg'),
('Морской Цезарь', 'Цезарь в сливочном соусе с креветками, морскими гребешками и рыбой', '4.7', 14.99, 1, 'cezarKrev.jpg'),
('Тирамису', 'Классический итальянский десерт с маскарпоне', '4.8', 6.50, 5, 'tiramisu.jpg'),
('Лимонад', 'Освежающий напиток с натуральным лимонным соком', '4.0', 3.99, 6, 'lemonade.jpg'),
('Морс', 'Натуральный напиток из свежих ягод', '4.5', 4.50, 6, 'mors.jpg');

INSERT INTO public.menu (name, description, rate, price, category, photo) VALUES
('Сёмга на гриле', 'Нежная сёмга, приготовленная на углях с лимонно-травяным маслом', '4.9', 15.99, 1, 'semga.jpg'),
('Тунец стейк', 'Стейк из тунца с соусом терияки и свежими овощами', '4.8', 17.99, 1, 'tunets.jpg'),
('Креветки в чесночном масле', 'Жареные креветки в ароматном чесночном масле с зеленью', '4.6', 12.50, 2, 'krevetki.jpg'),
('Кальмары гриль', 'Маринованные кальмары на гриле с лимонным соком', '4.7', 10.99, 2, 'kalmary.jpg'),
('Греческий салат', 'Классический салат с свежими овощами, оливками и фетой', '4.5', 8.99, 3, 'greek.jpg'),
('Цезарь с креветками', 'Салат Цезарь с крупными креветками, сухариками и пармезаном', '4.8', 9.99, 3, 'cezarShrimp.jpg'),
('Суп из морепродуктов', 'Богатый суп с миксом морепродуктов, кремом и пряностями', '4.5', 13.99, 1, 'seafoodSoup.jpg'),
('Устрицы по-рокфеллеровски', 'Запеченные устрицы с шпинатом, сыром и мускатным орехом', '4.9', 22.50, 2, 'oysters.jpg'),
('Фруктовый сок', 'Свежевыжатый сок из выбора сезонных фруктов', '4.4', 4.50, 5, 'fruitJuice.jpg'),
('Кофе эспрессо', 'Крепкий эспрессо, приготовленный из свежемолотых кофейных зерен', '4.7', 2.99, 6, 'espresso.jpg');
