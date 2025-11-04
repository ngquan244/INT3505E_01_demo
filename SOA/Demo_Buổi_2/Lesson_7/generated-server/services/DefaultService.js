/* eslint-disable no-unused-vars */
const Service = require('./Service');
const { connectDB, sql } = require('../utils/db');

/**
 * Get all products
 */
const getProducts = () => new Promise(async (resolve, reject) => {
  try {
    const pool = await connectDB();
    const result = await pool.request().query('SELECT * FROM Products');
    resolve(Service.successResponse(result.recordset));
  } catch (e) {
    console.error('ERROR getProducts:', e);
    reject(Service.rejectResponse(e.message || 'Database error', 500));
  }
});



const getProductById = ({ id }) => new Promise(async (resolve, reject) => {
  if (!id) return reject(Service.rejectResponse('Missing required field: id', 400));

  try {
    const pool = await connectDB();
    console.log('DEBUG ID received:', id);  
    const result = await pool.request()
      .input('id', sql.UniqueIdentifier, id)
      .query('SELECT * FROM Products WHERE id=@id');
    console.log('DEBUG query result:', result.recordset); 
    if (result.recordset.length === 0) {
      reject(Service.rejectResponse('Product not found', 404));
    } else {
      resolve(Service.successResponse(result.recordset[0]));
    }
  } catch (e) {
    console.error('ERROR getProductById:', e);
    reject(Service.rejectResponse(e.message || 'Database error', 500));
  }
});


/**
 * Create a new product
 */
const createProduct = ({ name, price, inStock }) => new Promise(async (resolve, reject) => {
  if (!name || price === undefined || inStock === undefined) {
    return reject(Service.rejectResponse('Missing required fields', 400));
  }

  try {
    const pool = await connectDB();
    const result = await pool.request()
      .input('name', sql.NVarChar(100), name)
      .input('price', sql.Float, price)
      .input('inStock', sql.Bit, inStock)
      .query('INSERT INTO Products (name, price, inStock) OUTPUT INSERTED.* VALUES (@name, @price, @inStock)');
    resolve(Service.successResponse(result.recordset[0]));
  } catch (e) {
    reject(Service.rejectResponse(e.message || 'Insert failed', 500));
  }
});




/**
 * Update a product
 */
const updateProduct = ({ id, name, price, inStock }) => new Promise(async (resolve, reject) => {
  if (!id || !name || price === undefined || inStock === undefined) {
    return reject(Service.rejectResponse('Missing required fields', 400));
  }

  try {
    const pool = await connectDB();
    await pool.request()
      .input('id', sql.UniqueIdentifier, id)
      .input('name', sql.NVarChar(100), name)
      .input('price', sql.Float, price)
      .input('inStock', sql.Bit, inStock)
      .query('UPDATE Products SET name=@name, price=@price, inStock=@inStock WHERE id=@id');

    resolve(Service.successResponse({ message: 'Updated successfully' }));
  } catch (e) {
    reject(Service.rejectResponse(e.message || 'Update failed', 500));
  }
});


/**
 * Delete a product
 */
const deleteProduct = ({ id }) => new Promise(async (resolve, reject) => {
  if (!id) {
    return reject(Service.rejectResponse('Missing required field: id', 400));
  }

  try {
    const pool = await connectDB();
    await pool.request()
      .input('id', sql.UniqueIdentifier, id)
      .query('DELETE FROM Products WHERE id=@id');

    resolve(Service.successResponse({ message: 'Deleted successfully' }));
  } catch (e) {
    reject(Service.rejectResponse(e.message || 'Delete failed', 500));
  }
});



module.exports = {
  createProduct,
  deleteProduct,
  getProductById,
  getProducts,
  updateProduct,
};
