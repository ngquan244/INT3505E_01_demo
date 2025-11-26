const express = require("express");
const router = express.Router();
const deprecate = require("../middleware/deprecation");

router.use(
  deprecate({
    sunset: "2026-06-01T00:00:00Z",
    successor: "/api/v2/payments",
    message: "Payments API v1 is deprecated and will be removed on 2026-06-01"
  })
);

router.post("/", (req, res) => {
  const { amount, currency, card_number, cvv } = req.body;

  if (!card_number || !cvv) {
    return res.status(400).json({ error: "card_number & cvv are required" });
  }

  res.json({
    payment_id: "pay_v1_xxx",
    status: "success",
    amount,
    currency,
    notice: "This is deprecated v1. Please migrate to v2."
  });
});

module.exports = router;
