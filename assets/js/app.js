import Alpine from "alpinejs";
import collapse from "@alpinejs/collapse";
import focus from "@alpinejs/focus";
import htmx from "htmx.org";

Alpine.plugin(collapse);
Alpine.plugin(focus);

window.Alpine = Alpine;
window.htmx = htmx;

Alpine.start();
