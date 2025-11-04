const sql = require('mssql');

const config = {
  server: "244-NGUYEN-QUAN\\SQL2022",
  database: "Book",
  driver: "ODBC Driver 17 for SQL Server",
  options: {
    trustedConnection: true,
    encrypt: false
  }
};

async function getPool() {
  if (global.pool) return global.pool;
  global.pool = await sql.connect(config);
  return global.pool;
}

module.exports = { sql, getPool };
