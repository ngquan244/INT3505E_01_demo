module.exports = function deprecate(versionInfo) {
  return function (req, res, next) {
    res.setHeader("Deprecation", "true");
    res.setHeader("Sunset", versionInfo.sunset);
    res.setHeader("Link", `<${versionInfo.successor}>; rel="successor-version"`);
    res.setHeader(
      "Warning",
      `299 - "${versionInfo.message}"`
    );
    next();
  };
};
