const express = require("express");
const router = express.Router();
const idempotency = require("../utils/idempotency");

router.post("/", (req, res) => {
  const { amount, currency, payment_method_id } = req.body;
  const idempotency_key = req.headers["idempotency-key"]; // lấy từ header

  if (!payment_method_id) {
    return res.status(400).json({ error: "payment_method_id is required" });
  }

  if (!idempotency_key) {
    return res.status(400).json({ error: "Idempotency-Key header is required" });
  }

  const response = idempotency(idempotency_key, () => ({
    payment_id: "pay_v2_xxx",
    status: "success",
    amount,
    currency,
    processed_at: new Date().toISOString(),
  }));

  res.json(response);
});

module.exports = router;
