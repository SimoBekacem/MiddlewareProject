const express = require('express');
const cors = require('cors');
const birdsRoutes = require('./routes/birds.route');

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api', birdsRoutes);

module.exports = app;
