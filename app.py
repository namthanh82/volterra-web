from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "volterra-dev-secret"

LANGUAGES = {
    "vi": {
        "name": "Tiếng Việt",
        "welcome": "Chào mừng đến với Volterra",
        "subtitle": "AI driven and more for EV charging infrastructure",
        "select_language": "Chọn ngôn ngữ",
        "continue": "Tiếp tục",
        "login": "Đăng nhập",
        "register": "Đăng ký",
        "dashboard": "Bảng điều khiển",
        "stations": "Trạm sạc",
        "bookings": "Lịch đặt chỗ",
        "reports": "Báo cáo",
        "monitor": "Giám sát",
        "maintenance": "Bảo trì",
        "settings": "Cài đặt",
        "manager_portal": "Cổng quản lý",
        "online": "Đang hoạt động",
        "offline": "Ngoại tuyến",
        "reserved": "Đã đặt",
        "charging": "Đang sạc",
    },
    "en": {
        "name": "English",
        "welcome": "Welcome to Volterra",
        "subtitle": "EV charging management platform for station owners and operators.",
        "select_language": "Select language",
        "continue": "Continue",
        "login": "Login",
        "register": "Register",
        "dashboard": "Dashboard",
        "stations": "Stations",
        "bookings": "Bookings",
        "reports": "Reports",
        "monitor": "Monitor",
        "maintenance": "Maintenance",
        "settings": "Settings",
        "manager_portal": "Manager Portal",
        "online": "Online",
        "offline": "Offline",
        "reserved": "Reserved",
        "charging": "Charging",
    },
}

DASHBOARD_METRICS = [
    {"label": "Tổng trạm", "value": 12, "trend": "+2 trong tháng"},
    {"label": "Cổng sạc hoạt động", "value": 48, "trend": "92% uptime"},
    {"label": "Booking hôm nay", "value": 126, "trend": "+14% so với hôm qua"},
    {"label": "Doanh thu tháng", "value": "128.4M", "trend": "Ước tính"},
]

DASHBOARD_CARDS = [
    {"name": "Volterra-11", "model": "Vin Bus", "tone": "orange", "state": "finished"},
    {"name": "Volterra-15", "model": "Vin Bus", "tone": "orange", "state": "finished"},
    {"name": "Volterra-17", "model": "Vin Bus", "tone": "orange", "state": "finished"},
    {"name": "Volterra-1", "model": "Vin Car", "tone": "green", "state": "charging"},
    {"name": "Volterra-2", "model": "Vin Car", "tone": "green", "state": "charging"},
    {"name": "Volterra-3", "model": "Vin Car", "tone": "green", "state": "charging"},
    {"name": "Volterra-4", "model": "Vin Car", "tone": "green", "state": "charging"},
    {"name": "Volterra-16", "model": "Vin Bus", "tone": "orange", "state": "finished"},
    {"name": "Volterra-5", "model": "Vin Bus", "tone": "dark", "state": "charging"},
    {"name": "Volterra-12", "model": "Vin Bus", "tone": "green", "state": "charging"},
    {"name": "Volterra-10", "model": "Vin Bus", "tone": "green", "state": "charging"},
]


POPUP_CONNECTOR_STATE = {
    "Volterra-11": ["Occupied", "Occupied"],
    "Volterra-15": ["Occupied", "Occupied"],
    "Volterra-17": ["Occupied", "Occupied"],
    "Volterra-16": ["Occupied", "Occupied"],
    "Volterra-1": ["Occupied", "Ready"],
    "Volterra-2": ["Occupied", "Ready"],
    "Volterra-3": ["Occupied", "Ready"],
    "Volterra-4": ["Occupied", "Ready"],
    "Volterra-5": ["Occupied", "Ready"],
    "Volterra-12": ["Occupied", "Ready"],
    "Volterra-10": ["Occupied", "Ready"],
}

STATION_VEHICLE_IMAGE = {
    "Volterra-11": "images/bus.png",
    "Volterra-15": "images/bus.png",
    "Volterra-17": "images/bus.png",
    "Volterra-16": "images/bus.png",
    "Volterra-1": "images/oto.png",
    "Volterra-2": "images/oto.png",
    "Volterra-3": "images/oto.png",
    "Volterra-4": "images/oto.png",
    "Volterra-5": "images/bus.png",
    "Volterra-12": "images/bus.png",
    "Volterra-10": "images/bus.png",
}

# Booked charging duration (minutes) per connector [Connector A, Connector B]
VEHICLE_BOOKED_DURATION = {
    "Volterra-11": [120, 120],
    "Volterra-15": [90, 90],
    "Volterra-17": [120, 90],
    "Volterra-16": [60, 75],
    "Volterra-1": [85, 0],
    "Volterra-2": [60, 0],
    "Volterra-3": [49, 0],
    "Volterra-4": [27, 0],
    "Volterra-5": [105, 0],
    "Volterra-12": [70, 0],
    "Volterra-10": [80, 0],
}

STATION_DETAILS = {
    "Volterra-11": {"site": "Solar hub A", "source": "Solar + BESS", "charge_type": "Fast", "power": "120 kW", "voltage": "715 V", "current": "167 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Ready", "Ready"]},
    "Volterra-15": {"site": "Solar hub A", "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "698 V", "current": "89 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Ready", "Ready"]},
    "Volterra-17": {"site": "Solar hub B", "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "702 V", "current": "91 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Ready", "Ready"]},
    "Volterra-1": { "source": "BESS + Grid", "charge_type": "Fast", "power": "120 kW", "voltage": "688 V", "current": "175 A", "soc": "78%", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-2": { "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "705 V", "current": "86 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-3": { "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "709 V", "current": "88 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-4": { "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "712 V", "current": "92 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-16": {"site": "Solar hub B", "source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "710 V", "current": "90 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Ready", "Ready"]},
    "Volterra-5": { "source": "BESS", "charge_type": "Fast", "power": "120 kW", "voltage": "681 V", "current": "162 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-12": {"source": "Solar + BESS", "charge_type": "Slow", "power": "60 kW", "voltage": "706 V", "current": "85 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
    "Volterra-10": {"source": "Solar", "charge_type": "Slow", "power": "60 kW", "voltage": "707 V", "current": "87 A", "connectors": ["Connector A", "Connector B"], "connector_status": ["Charging", "Ready"]},
}

STATIONS = [
    {"name": "Volterra Central", "city": "Hà Nội", "status": "charging", "chargers": "8/10"},
    {"name": "Volterra West", "city": "Hồ Chí Minh", "status": "online", "chargers": "12/12"},
    {"name": "Volterra East", "city": "Đà Nẵng", "status": "reserved", "chargers": "5/8"},
    {"name": "Volterra Express", "city": "Hải Phòng", "status": "offline", "chargers": "0/6"},
]

BOOKINGS = [
    {"driver": "Nguyễn An", "station": "Volterra Central", "time": "09:00", "status": "Đang chờ"},
    {"driver": "Trần Bình", "station": "Volterra West", "time": "09:30", "status": "Đã xác nhận"},
    {"driver": "Lê Chi", "station": "Volterra East", "time": "10:00", "status": "Đang sạc"},
]

REPORTS = [
    {"label": "Tỷ lệ sử dụng", "value": "78%"},
    {"label": "Thời gian chờ trung bình", "value": "11 phút"},
    {"label": "Sự cố trong tuần", "value": "3"},
]


def current_language():
    code = session.get("lang", "vi")
    return LANGUAGES.get(code, LANGUAGES["vi"])


@app.context_processor
def inject_globals():
    code = session.get("lang", "vi")
    return {"lang_code": code, "lang": current_language(), "languages": LANGUAGES}


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.post("/set-language")
def set_language():
    session["lang"] = request.form.get("lang", "vi")
    next_url = request.form.get("next") or url_for("index")
    return redirect(next_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["logged_in"] = True
        session["user_name"] = request.form.get("email", "Manager")
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["logged_in"] = True
        session["user_name"] = request.form.get("name", "Manager")
        session["lang"] = request.form.get("lang", session.get("lang", "vi"))
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    selected = request.args.get("station")
    selected_card = next((card for card in DASHBOARD_CARDS if card["name"] == selected), None) if selected else None
    selected_detail = STATION_DETAILS.get(selected_card["name"]) if selected_card else None
    return render_template(
        "dashboard.html",
        reports=REPORTS,
        dashboard_cards=DASHBOARD_CARDS,
        popup_connector_state=POPUP_CONNECTOR_STATE,
        station_details=STATION_DETAILS,
        station_vehicle_image=STATION_VEHICLE_IMAGE,
        vehicle_booked_duration=VEHICLE_BOOKED_DURATION,
        selected_station=selected_card,
        selected_detail=selected_detail,
        active_tab="dashboard",
    )


@app.route("/reports")
def reports():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("reports.html", reports=REPORTS, active_tab="reports")


@app.route("/monitor")
def monitor():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("monitor.html", active_tab="monitor")


@app.route("/maintenance")
def maintenance():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("maintenance.html", active_tab="maintenance")


@app.route("/settings")
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("settings.html", active_tab="settings")


@app.route("/optimize")
def optimize():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("optimize.html", active_tab="optimize")


if __name__ == "__main__":
    app.run(debug=True)
