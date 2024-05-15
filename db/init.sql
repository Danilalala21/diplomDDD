-- Insert users
INSERT INTO public.users (email, password, lastname, firstname, password_changed, status, role)
VALUES
('admin@example.com', 'pbkdf2:sha256:260000$80VZTW7RYOnHqqW3$09209afff6f694733175063c16c8d865f820c1455fb668d3244838dc192f70ba', 'Admin', 'User', true, true, 1),
('customer@example.com', 'pbkdf2:sha256:260000$80VZTW7RYOnHqqW3$09209afff6f694733175063c16c8d865f820c1455fb668d3244838dc192f70ba', 'Customer', 'User', true, true, 2),
('staff@example.com', 'pbkdf2:sha256:260000$80VZTW7RYOnHqqW3$09209afff6f694733175063c16c8d865f820c1455fb668d3244838dc192f70ba', 'Staff', 'User', true, true, 3);


-- Insert orders
INSERT INTO public.orders ("user", "time", summa, "table", status)
VALUES
(2, CURRENT_TIMESTAMP, 15.98, NULL, 1),
(2, CURRENT_TIMESTAMP, 10.99, NULL, 2),
(3, CURRENT_TIMESTAMP, 7.99, NULL, 1);

-- Insert comments
INSERT INTO public.comments ("user", food, comment, "time") VALUES
(2, 1, 'The burger was amazing!', CURRENT_TIMESTAMP),
(2, 2, 'Pizza was a bit too greasy for my taste', CURRENT_TIMESTAMP),
(3, 3, 'Great salad, fresh ingredients', CURRENT_TIMESTAMP);