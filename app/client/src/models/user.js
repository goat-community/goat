export class User {
  constructor(
    name,
    surname,
    email,
    password,
    is_active,
    active_study_area,
    organization_id,
    storage
  ) {
    this.name = name;
    this.surname = surname;
    this.email = email;
    this.password = password;
    this.is_active = is_active;
    this.active_study_area = active_study_area;
    this.organization_id = organization_id;
    this.storage = storage;
  }
}
