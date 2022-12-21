const dimmer = document.getElementById("external-led-dimmer");
dimmer.addEventListener("change", async (e) => {
  try {
    await fetch("/api/external_led_dimmer/", {
      method: "POST",
      body: JSON.stringify({
        brightness: e.target.value,
      }),
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
});

const pulse = document.getElementById("external-led-pulse");
pulse.addEventListener("change", async (e) => {
  try {
    await fetch("/api/external_led_pulse/", {
      method: "POST",
      body: JSON.stringify({
        rate: e.target.value,
      }),
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
});

const offButton = document.getElementById("external-led-off");
offButton.addEventListener("click", async (_) => {
  try {
    await fetch("/api/stop_pulse/", {
      method: "POST",
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
});
