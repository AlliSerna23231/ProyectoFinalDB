DROP TABLE USUARIO;
DROP TABLE PUBLICACION;
DROP TABLE ME_GUSTA;
DROP TABLE COMENTARIO;
DROP TABLE MENSAJE;
DROP TABLE AMISTAD;


CREATE TABLE USUARIO(
    id_us int PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    correo VARCHAR(100),
    password VARCHAR(250),
    fecha_nac DATE,
    ubicacion VARCHAR(100)
);


CREATE TABLE PUBLICACION(
    id_publicacion int AUTO_INCREMENT PRIMARY KEY,
    id_us int,
    titulo VARCHAR(50),
    contenido VARCHAR(1000),
    fecha_pub DATE,
    hora_pub TIME,
    CONSTRAINT fk_publicacion_id_us FOREIGN KEY (id_us) REFERENCES USUARIO(id_us)
);

CREATE TABLE ME_GUSTA(
    id_megusta int AUTO_INCREMENT PRIMARY KEY,
    id_us int,
    id_publicacion int,
    CONSTRAINT fk_megusta_id_us FOREIGN KEY (id_us) REFERENCES USUARIO(id_us),
    CONSTRAINT fd_megusta_id_publicacion FOREIGN KEY (id_publicacion) REFERENCES PUBLICACION(id_publicacion)
);

CREATE TABLE COMENTARIO(
    id_coment int AUTO_INCREMENT PRIMARY KEY,
    id_us int,
    id_publicacion int,
    contenido VARCHAR(1000),
    fec_pub DATE,
    CONSTRAINT fk_coment_id_us FOREIGN KEY (id_us) REFERENCES USUARIO(id_us),
    CONSTRAINT fd_coment_id_publicacion FOREIGN KEY (id_publicacion) REFERENCES PUBLICACION(id_publicacion)
);


CREATE TABLE MENSAJE(
    id_mes int AUTO_INCREMENT PRIMARY KEY,
    id_us int,
    id_us2 int,
    contenido VARCHAR(1000),
    fec_envio DATE,
    CONSTRAINT fk_mes_id_us FOREIGN KEY (id_us) REFERENCES USUARIO(id_us)
);

CREATE TABLE AMISTAD(
    id_amis int AUTO_INCREMENT PRIMARY KEY,
    id_us int,
    id_us2 int,
    CONSTRAINT fk_amistad_id_us FOREIGN KEY (id_us) REFERENCES USUARIO(id_us)
);

