// Sends your time zone along with the sign-in, so "due today" means today where you are. Nothing else.
(function () {
  "use strict";
  try {
    const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (zone) document.getElementById("signin").href = "/signin?tz=" + encodeURIComponent(zone);
  } catch (err) { /* the default time zone is used */ }
})();
