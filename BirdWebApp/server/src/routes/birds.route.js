const express = require('express');
const router = express.Router();
const { getBirdsList } = require('../routes/birds.controler');

// Define the route to get the birds list
router.get('/birds', getBirdsList);

module.exports = router;
