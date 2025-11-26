const swaggerUi = require("swagger-ui-express");
const fs = require("fs");
const yaml = require("js-yaml");

module.exports = (app) => {
  const swaggerDocument = yaml.load(fs.readFileSync("./swagger.yaml", "utf8"));
  app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));
};
