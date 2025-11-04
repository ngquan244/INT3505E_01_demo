// utils/db.js
const sql = require('mssql');

const config = {
  user: 'sa',       
  password: 'acb12343234', 
  server: '244-NGUYEN-QUAN\\SQL2022',
  database: 'Product', 
  options: {
    encrypt: false,  
    trustServerCertificate: true
  },
  pool: {
    max: 10,
    min: 0,
    idleTimeoutMillis: 30000
  }
};

let pool;

async function connectDB() {
  if (pool) return pool;
  pool = await sql.connect(config);
  return pool;
}

module.exports = { connectDB, sql };
