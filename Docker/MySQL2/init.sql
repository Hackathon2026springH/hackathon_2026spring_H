DROP DATABASE IF EXISTS snsapp;

DROP USER IF EXISTS 'testuser'@'%';


CREATE USER 'testuser'@'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS snsapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;


GRANT ALL PRIVILEGES ON snsapp.* TO 'testuser'@'%';

FLUSH PRIVILEGES;

USE snsapp;

CREATE TABLE
    users (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_name VARCHAR(255) NOT NULL,
        email_address VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    weights_and_BFP (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_id BINARY(16) NOT NULL,
        weights FLOAT NOT NULL,
        BFP FLOAT NOT NULL,
        measured_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        CONSTRAINT fk_weights_and_BFP_user FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    follow_users (
        user_id BINARY(16) NOT NULL,
        following_user_id BINARY(16) NOT NULL,
        PRIMARY KEY (user_id, following_user_id),
        CONSTRAINT fk_follow_users_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_follow_users_following_user FOREIGN KEY (following_user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    themes (
        id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
        theme_name VARCHAR(255) NOT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    threads (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_id BINARY(16) NOT NULL,
        title VARCHAR(255) NOT NULL,
        image VARCHAR(255),
        theme_id INT UNSIGNED NOT NULL,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME(6) DEFAULT NULL,
        CONSTRAINT fk_threads_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_threads_theme FOREIGN KEY (theme_id) REFERENCES themes (id),
        KEY idx_threads_user_id (user_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    reactions (
        id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
        reaction_name VARCHAR(255) NOT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    theme_reactions (
        theme_id INT UNSIGNED NOT NULL,
        reaction_id INT UNSIGNED NOT NULL,
        PRIMARY KEY (theme_id, reaction_id),
        CONSTRAINT fk_theme_reactions_theme FOREIGN KEY (theme_id) REFERENCES themes (id),
        CONSTRAINT fk_theme_reactions_reaction FOREIGN KEY (reaction_id) REFERENCES reactions (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    thread_reactions (
        user_id BINARY(16) NOT NULL,
        thread_id BINARY(16) NOT NULL,
        reaction_id INT UNSIGNED NOT NULL,
        reaction_count INT UNSIGNED,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (user_id, thread_id, reaction_id),
        CONSTRAINT reaction_count_limit CHECK (reaction_count <= 100),
        CONSTRAINT fk_thread_reactions_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_thread_reactions_thread FOREIGN KEY (thread_id) REFERENCES threads (id),
        CONSTRAINT fk_thread_reactions_reaction FOREIGN KEY (reaction_id) REFERENCES reactions (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    posts (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_id BINARY(16) NOT NULL,
        thread_id BINARY(16) NOT NULL,
        content TEXT NOT NULL,
        image VARCHAR(255),
        count SMALLINT UNSIGNED NOT NULL,
        rep SMALLINT UNSIGNED,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME(6) DEFAULT NULL,
        CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_posts_thread FOREIGN KEY (thread_id) REFERENCES threads (id),
        KEY idx_posts_user_id (user_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    comments (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_id BINARY(16) NOT NULL,
        thread_id BINARY(16) NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME(6) DEFAULT NULL,
        CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_comments_thread FOREIGN KEY (thread_id) REFERENCES threads (id),
        KEY idx_comments_user_id (user_id),
        KEY idx_comments_thread_id (thread_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    tweets (
        id BINARY(16) NOT NULL PRIMARY KEY,
        user_id BINARY(16) NOT NULL,
        thread_id BINARY(16),
        content TEXT NOT NULL,
        created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME(6) DEFAULT NULL,
        CONSTRAINT fk_tweets_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_tweets_thread FOREIGN KEY (thread_id) REFERENCES threads (id),
        KEY idx_tweets_user_id (user_id),
        KEY idx_tweets_thread_id (thread_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

INSERT INTO themes (id, theme_name)
VALUES (1, '応援して!'), (2, '喝入れて!');

INSERT INTO reactions (id, reaction_name)
VALUES (1, 'がんばれ!'), (2, 'すごい!'), (3, 'いいぞ!'), (4, '喝!'), (5, 'もっとやれる!'), (6, 'まだまだ!');

INSERT INTO theme_reactions (theme_id, reaction_id)
VALUES (1, 1), (1, 2), (1, 3), (2, 4), (2, 5), (2, 6);


INSERT INTO users (id, user_name, email_address, password)
VALUES 
    (UUID_TO_BIN('31f56aaf-e51c-42d0-a1cf-755d5c55d14f'), '山田太郎', 'taro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
    (UUID_TO_BIN('ce316f18-a725-4ea8-8cc4-ef3706130dca'), '鈴木二郎', 'jiro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244');

INSERT INTO threads (id, user_id, title, theme_id)
VALUES
    (UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'),
     UUID_TO_BIN('31f56aaf-e51c-42d0-a1cf-755d5c55d14f'), '毎日腕立て30回!', 1),
    (UUID_TO_BIN('aeba0b0b-be5a-4d72-b243-69980e006b49'),
     UUID_TO_BIN('ce316f18-a725-4ea8-8cc4-ef3706130dca'), '毎日スクワット40回!', 2);

INSERT INTO posts (id, user_id, thread_id, content, number)
VALUES
    (UUID_TO_BIN('ff77fb5d-2a07-422c-9b5e-7142a841ea39'),
     UUID_TO_BIN('31f56aaf-e51c-42d0-a1cf-755d5c55d14f'),
     UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'), '1日目、目標達成!', 30),
    (UUID_TO_BIN('eabf7f76-88e7-4ce7-ba81-6c290ace1cc2'),
     UUID_TO_BIN('31f56aaf-e51c-42d0-a1cf-755d5c55d14f'),
     UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'), '2日目、目標達成!', 30),
    (UUID_TO_BIN('126e4e3a-670a-4840-aa4d-70c8d4261bd9'),
     UUID_TO_BIN('31f56aaf-e51c-42d0-a1cf-755d5c55d14f'),
     UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'), '3日目、目標達成ならず...',20);

INSERT INTO comments (id, user_id, thread_id, content)
VALUES
    (UUID_TO_BIN('de21a1c4-78f6-4bf5-ad88-25cc7abec868'),
     UUID_TO_BIN('ce316f18-a725-4ea8-8cc4-ef3706130dca'),
     UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'), '応援しています！頑張ってください。');

INSERT INTO thread_reactions (user_id, thread_id, reaction_id, reaction_count)
VALUES
    (UUID_TO_BIN('ce316f18-a725-4ea8-8cc4-ef3706130dca'),
     UUID_TO_BIN('70f080de-a87f-4776-8961-3a4bec011886'), 1, 1);