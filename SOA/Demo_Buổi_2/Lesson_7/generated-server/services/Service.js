class Service {
  static rejectResponse(message, code = 500) {
    const errorPayload = (message && typeof message === 'object' && !Array.isArray(message))
      ? message
      : { message: String(message) };
    return { error: errorPayload, code };
  }

  static successResponse(payload) {
    return payload;
  }
}

module.exports = Service;
