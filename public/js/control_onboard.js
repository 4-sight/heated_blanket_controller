const onButton = document.getElementById("onboard-led-on");
onButton.addEventListener("click", async (_) => {
  try {
    await fetch("/api/onboard_led/", {
      method: "POST",
      body: JSON.stringify({
        led: true,
      }),
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
});

const offButton = document.getElementById("onboard-led-off");
offButton.addEventListener("click", async (_) => {
  try {
    await fetch("/api/onboard_led/", {
      method: "POST",
      body: JSON.stringify({
        led: false,
      }),
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
});
