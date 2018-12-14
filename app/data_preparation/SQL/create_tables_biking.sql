--biking relevant tables
drop table if exists way_type_factor;
CREATE TABLE way_type_factor
(
  class_id integer primary key,
  way_type_factor numeric
);

insert into way_type_factor
values(100, 1),(101, 8),(102, 2.06),(103, 8),(104, 7.47),(105, 2.06),(106, 2.06),(107, 2.06),(108, 1.5),
(109, 1),(110, 0.98),(111, 0.9),(112, 1.1),(113, 1.3),(114, 0.9),(115, 1.1),(116, 1),
(117, 0.75),(118 ,0.6),(119, 1.1),(120, 1.3),(121, 1.3),(122, 8),(123, 1),(124, 1.5),(125, 1),
(201, 0.87),(202, 0.73),(203, 0.87),(204, 0.87),(301, 1),(302, 1.18),(303, 1.5),(304, 3),(305, 4),(401, 1);


drop table if exists surface_factor;
CREATE TABLE surface_factor
(
  surface varchar(50) primary key,
  surface_factor numeric
);

insert into surface_factor
values('paved', 1), ('asphalt', 1), ('sett', 1.5), ('ballast', 1.5), ('paving_stones', 1.5), ('unpaved', 1.18),
('cobblestone', 1.5), ('dirt', 1.5), ('grass', 1.5), ('gravel', 1.5);