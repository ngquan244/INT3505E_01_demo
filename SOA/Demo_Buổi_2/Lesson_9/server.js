const express = require("express");
const app = express();
app.use(express.json());

// ---------- ROUTES ----------
app.use("/api/v1/payments", require("./routes/payments.v1"));
app.use("/api/v2/payments", require("./routes/payments.v2"));

// ---------- SWAGGER ----------
require("./swagger")(app);

// ---------- START SERVER ----------
app.listen(3000, () => {
  console.log("Server running at http://localhost:3000");
  console.log("Swagger UI: http://localhost:3000/api-docs");
});
