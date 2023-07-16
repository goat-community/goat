import React from "react";

import AuthTemplate from "./AuthTemplate";
import Create from "./steps/Create";

const OrganizationCreation = () => {
  return (
    <AuthTemplate>
      <Create />
    </AuthTemplate>
  );
};

export default OrganizationCreation;
