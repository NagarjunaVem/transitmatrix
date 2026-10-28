# PowerShell Seed Generator for TransitMatrix
# Generates realistic, referentially valid SQL seed data matching DBMS requirements

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("-- =============================================================================")
[void]$sb.AppendLine("-- TransitMatrix: Comprehensive Seed Data (Referentially Valid)")
[void]$sb.AppendLine("-- Storage Engine: InnoDB / MySQL 8.0+")
[void]$sb.AppendLine("-- Minimums: >=30 Stations, >=15 Routes, >=20 Services, >=100 Trips,")
[void]$sb.AppendLine("--           >=200 Passengers, >=500 Bookings, plus Tickets, Inventory,")
[void]$sb.AppendLine("--           Payments, Cancellations, Delays, Waitlists, Predictions")
[void]$sb.AppendLine("-- =============================================================================")
[void]$sb.AppendLine()
[void]$sb.AppendLine("USE transitmatrix;")
[void]$sb.AppendLine("SET FOREIGN_KEY_CHECKS = 0;")
[void]$sb.AppendLine()

# 1. USERS (25 users: 3 admins, 4 staff, 18 passengers)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 1. USERS (25 records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO users (user_id, username, email, password_hash, role, first_name, last_name, phone_number, is_active) VALUES")
$usersList = @(
    "('1', 'admin_sys', 'admin@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'ADMIN', 'System', 'Administrator', '+919876543201', 1)",
    "('2', 'admin_ops', 'ops.admin@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'ADMIN', 'Operations', 'Head', '+919876543202', 1)",
    "('3', 'admin_audit', 'audit@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'ADMIN', 'Security', 'Auditor', '+919876543203', 1)",
    "('4', 'staff_ndls', 'counter1.ndls@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'STAFF', 'Rajesh', 'Kumar', '+919876543204', 1)",
    "('5', 'staff_bct', 'counter1.bct@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'STAFF', 'Suresh', 'Patil', '+919876543205', 1)",
    "('6', 'staff_hwh', 'counter1.hwh@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'STAFF', 'Subhash', 'Banerjee', '+919876543206', 1)",
    "('7', 'staff_mas', 'counter1.mas@transitmatrix.org', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'STAFF', 'Murugan', 'Sundaram', '+919876543207', 1)"
)
for ($i = 8; $i -le 25; $i++) {
    $fn = @("Aman", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Rohan", "Pooja", "Karan", "Kavita", "Siddharth", "Neha", "Arjun", "Divya", "Aditya", "Ritu", "Gaurav", "Meera")[$i - 8]
    $ln = @("Sharma", "Verma", "Gupta", "Singh", "Malhotra", "Mehta", "Iyer", "Nair", "Reddy", "Patel", "Joshi", "Chopra", "Das", "Bose", "Saxena", "Deshmukh", "Choudhury", "Pillai")[$i - 8]
    $usersList += "('$i', 'user_$i', 'user$i@gmail.com', '`$2b`$12`$e87.gK/xV37rYc48vW5lseCqB2d3A.qWb1wXpMh2YvK.o98zZkQCe', 'PASSENGER', '$fn', '$ln', '+9198765432$($i.ToString('00'))', 1)"
}
[void]$sb.AppendLine(($usersList -join ",`n") + ";`n")

# 2. STATIONS (35 stations)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 2. STATIONS (35 records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO stations (station_id, station_code, station_name, city, state, zone, total_platforms, latitude, longitude, is_active) VALUES")
$stationsData = @(
    "('1', 'NDLS', 'New Delhi', 'New Delhi', 'Delhi', 'Northern Railway', 16, 28.6424000, 77.2195000, 1)",
    "('2', 'BCT', 'Mumbai Central', 'Mumbai', 'Maharashtra', 'Western Railway', 9, 18.9696000, 72.8193000, 1)",
    "('3', 'CSMT', 'Chhatrapati Shivaji Maharaj Terminus', 'Mumbai', 'Maharashtra', 'Central Railway', 18, 18.9401000, 72.8347000, 1)",
    "('4', 'HWH', 'Howrah Junction', 'Kolkata', 'West Bengal', 'Eastern Railway', 23, 22.5839000, 88.3433000, 1)",
    "('5', 'MAS', 'MGR Chennai Central', 'Chennai', 'Tamil Nadu', 'Southern Railway', 17, 13.0827000, 80.2757000, 1)",
    "('6', 'SBC', 'KSR Bengaluru City', 'Bengaluru', 'Karnataka', 'South Western Railway', 10, 12.9784000, 77.5695000, 1)",
    "('7', 'HYB', 'Hyderabad Deccan', 'Hyderabad', 'Telangana', 'South Central Railway', 6, 17.3929000, 78.4691000, 1)",
    "('8', 'SC', 'Secunderabad Junction', 'Secunderabad', 'Telangana', 'South Central Railway', 10, 17.4344000, 78.5015000, 1)",
    "('9', 'ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat', 'Western Railway', 12, 23.0238000, 72.6011000, 1)",
    "('10', 'PUNE', 'Pune Junction', 'Pune', 'Maharashtra', 'Central Railway', 6, 18.5284000, 73.8744000, 1)",
    "('11', 'CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh', 'North Central Railway', 10, 26.4538000, 80.3513000, 1)",
    "('12', 'LKO', 'Lucknow Charbagh', 'Lucknow', 'Uttar Pradesh', 'Northern Railway', 9, 26.8322000, 80.9174000, 1)",
    "('13', 'BSB', 'Varanasi Junction', 'Varanasi', 'Uttar Pradesh', 'Northern Railway', 9, 25.3284000, 82.9866000, 1)",
    "('14', 'PNBE', 'Patna Junction', 'Patna', 'Bihar', 'East Central Railway', 10, 25.6022000, 85.1376000, 1)",
    "('15', 'AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh', 'North Central Railway', 6, 27.1591000, 78.0063000, 1)",
    "('16', 'BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh', 'West Central Railway', 6, 23.2685000, 77.4126000, 1)",
    "('17', 'NGP', 'Nagpur Junction', 'Nagpur', 'Maharashtra', 'Central Railway', 8, 21.1524000, 79.0888000, 1)",
    "('18', 'JAIP', 'Jaipur Junction', 'Jaipur', 'Rajasthan', 'North Western Railway', 8, 26.9196000, 75.7878000, 1)",
    "('19', 'CDG', 'Chandigarh Junction', 'Chandigarh', 'Chandigarh', 'Northern Railway', 6, 30.7018000, 76.8217000, 1)",
    "('20', 'JAT', 'Jammu Tawi', 'Jammu', 'Jammu and Kashmir', 'Northern Railway', 4, 32.7060000, 74.8797000, 1)",
    "('21', 'GHY', 'Guwahati Terminal', 'Guwahati', 'Assam', 'Northeast Frontier Railway', 7, 26.1822000, 91.7513000, 1)",
    "('22', 'TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala', 'Southern Railway', 5, 8.4871000, 76.9532000, 1)",
    "('23', 'ERS', 'Ernakulam Junction', 'Kochi', 'Kerala', 'Southern Railway', 6, 9.9676000, 76.2898000, 1)",
    "('24', 'GOA', 'Madgaon Junction', 'Madgaon', 'Goa', 'Konkan Railway', 4, 15.2736000, 73.9796000, 1)",
    "('25', 'BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh', 'South Central Railway', 10, 16.5186000, 80.6200000, 1)",
    "('26', 'VSKP', 'Visakhapatnam Junction', 'Visakhapatnam', 'Andhra Pradesh', 'East Coast Railway', 8, 17.7215000, 83.2867000, 1)",
    "('27', 'BBS', 'Bhubaneswar Terminal', 'Bhubaneswar', 'Odisha', 'East Coast Railway', 6, 20.2666000, 85.8436000, 1)",
    "('28', 'RNC', 'Ranchi Junction', 'Ranchi', 'Jharkhand', 'South Eastern Railway', 6, 23.3512000, 85.3346000, 1)",
    "('29', 'GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh', 'North Eastern Railway', 10, 26.7606000, 83.3732000, 1)",
    "('30', 'ASN', 'Asansol Junction', 'Asansol', 'West Bengal', 'Eastern Railway', 7, 23.6841000, 86.9746000, 1)",
    "('31', 'KGP', 'Kharagpur Junction', 'Kharagpur', 'West Bengal', 'South Eastern Railway', 12, 22.3381000, 87.3222000, 1)",
    "('32', 'GNT', 'Guntur Junction', 'Guntur', 'Andhra Pradesh', 'South Central Railway', 7, 16.3007000, 80.4428000, 1)",
    "('33', 'SVDK', 'Shri Mata Vaishno Devi Katra', 'Katra', 'Jammu and Kashmir', 'Northern Railway', 5, 32.9912000, 74.9317000, 1)",
    "('34', 'DLI', 'Old Delhi Junction', 'Delhi', 'Delhi', 'Northern Railway', 16, 28.6619000, 77.2274000, 1)",
    "('35', 'SHM', 'Shalimar Terminal', 'Howrah', 'West Bengal', 'South Eastern Railway', 5, 22.5562000, 88.3182000, 1)"
)
[void]$sb.AppendLine(($stationsData -join ",`n") + ";`n")

# 3. ROUTES (18 routes)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 3. ROUTES (18 records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO routes (route_id, route_code, route_name, origin_station_id, destination_station_id, total_distance_km, duration_est_minutes, is_active) VALUES")
$routesData = @(
    "('1', 'RT-NDLS-BCT', 'New Delhi - Mumbai Central Main Corridor', 1, 2, 1384.00, 960, 1)",
    "('2', 'RT-BCT-NDLS', 'Mumbai Central - New Delhi Return Corridor', 2, 1, 1384.00, 960, 1)",
    "('3', 'RT-NDLS-HWH', 'New Delhi - Howrah Grand Chord Corridor', 1, 4, 1447.00, 1020, 1)",
    "('4', 'RT-HWH-NDLS', 'Howrah - New Delhi Return Corridor', 4, 1, 1447.00, 1020, 1)",
    "('5', 'RT-NDLS-MAS', 'Grand Trunk North-South Corridor (NDLS - MAS)', 1, 5, 2175.00, 1680, 1)",
    "('6', 'RT-MAS-NDLS', 'Grand Trunk North-South Return Corridor (MAS - NDLS)', 5, 1, 2175.00, 1680, 1)",
    "('7', 'RT-BCT-ADI', 'Mumbai - Ahmedabad High Speed Link', 2, 9, 491.00, 360, 1)",
    "('8', 'RT-ADI-BCT', 'Ahmedabad - Mumbai High Speed Return Link', 9, 2, 491.00, 360, 1)",
    "('9', 'RT-SBC-MAS', 'Bengaluru - Chennai Express Corridor', 6, 5, 358.00, 270, 1)",
    "('10', 'RT-MAS-SBC', 'Chennai - Bengaluru Express Corridor', 5, 6, 358.00, 270, 1)",
    "('11', 'RT-CSMT-PUNE', 'Mumbai - Pune Ghat Intercity Route', 3, 10, 192.00, 180, 1)",
    "('12', 'RT-PUNE-CSMT', 'Pune - Mumbai Ghat Intercity Return Route', 10, 3, 192.00, 180, 1)",
    "('13', 'RT-NDLS-CDG', 'Delhi - Chandigarh Northern Intercity', 1, 19, 244.00, 210, 1)",
    "('14', 'RT-CDG-NDLS', 'Chandigarh - Delhi Northern Return Intercity', 19, 1, 244.00, 210, 1)",
    "('15', 'RT-HYB-BZA', 'Hyderabad - Vijayawada Deccan Express Route', 7, 25, 313.00, 300, 1)",
    "('16', 'RT-BZA-HYB', 'Vijayawada - Hyderabad Deccan Return Route', 25, 7, 313.00, 300, 1)",
    "('17', 'RT-NDLS-BSB', 'Delhi - Varanasi Holy City Superfast Link', 1, 13, 757.00, 480, 1)",
    "('18', 'RT-BSB-NDLS', 'Varanasi - Delhi Return Link', 13, 1, 757.00, 480, 1)"
)
[void]$sb.AppendLine(($routesData -join ",`n") + ";`n")

# 4. ROUTE STOPS (Sample stops for the 18 routes)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 4. ROUTE STOPS (Sequence mapping for corridors)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO route_stops (route_id, station_id, stop_sequence, distance_from_origin_km, departure_offset_minutes, arrival_offset_minutes, halt_duration_minutes, platform_number) VALUES")
$stopsData = @(
    # Route 1: NDLS -> BCT
    "(1, 1, 1, 0.00, 0, 0, 0, 1)",
    "(1, 16, 2, 705.00, 480, 470, 10, 2)",
    "(1, 2, 3, 1384.00, 960, 960, 0, 3)",
    # Route 2: BCT -> NDLS
    "(2, 2, 1, 0.00, 0, 0, 0, 3)",
    "(2, 16, 2, 679.00, 490, 480, 10, 1)",
    "(2, 1, 3, 1384.00, 960, 960, 0, 1)",
    # Route 3: NDLS -> HWH
    "(3, 1, 1, 0.00, 0, 0, 0, 2)",
    "(3, 11, 2, 440.00, 310, 300, 10, 4)",
    "(3, 13, 3, 757.00, 520, 510, 10, 1)",
    "(3, 14, 4, 998.00, 680, 670, 10, 2)",
    "(3, 4, 5, 1447.00, 1020, 1020, 0, 8)",
    # Route 4: HWH -> NDLS
    "(4, 4, 1, 0.00, 0, 0, 0, 8)",
    "(4, 14, 2, 449.00, 350, 340, 10, 3)",
    "(4, 13, 3, 690.00, 510, 500, 10, 2)",
    "(4, 11, 4, 1007.00, 710, 700, 10, 1)",
    "(4, 1, 5, 1447.00, 1020, 1020, 0, 2)",
    # Route 7: BCT -> ADI
    "(7, 2, 1, 0.00, 0, 0, 0, 1)",
    "(7, 9, 2, 491.00, 360, 360, 0, 2)",
    # Route 8: ADI -> BCT
    "(8, 9, 1, 0.00, 0, 0, 0, 2)",
    "(8, 2, 2, 491.00, 360, 360, 0, 1)",
    # Route 9: SBC -> MAS
    "(9, 6, 1, 0.00, 0, 0, 0, 1)",
    "(9, 5, 2, 358.00, 270, 270, 0, 4)",
    # Route 10: MAS -> SBC
    "(10, 5, 1, 0.00, 0, 0, 0, 4)",
    "(10, 6, 2, 358.00, 270, 270, 0, 1)",
    # Route 11: CSMT -> PUNE
    "(11, 3, 1, 0.00, 0, 0, 0, 5)",
    "(11, 10, 2, 192.00, 180, 180, 0, 2)",
    # Route 12: PUNE -> CSMT
    "(12, 10, 1, 0.00, 0, 0, 0, 2)",
    "(12, 3, 2, 192.00, 180, 180, 0, 5)",
    # Route 13: NDLS -> CDG
    "(13, 1, 1, 0.00, 0, 0, 0, 3)",
    "(13, 19, 2, 244.00, 210, 210, 0, 1)",
    # Route 14: CDG -> NDLS
    "(14, 19, 1, 0.00, 0, 0, 0, 1)",
    "(14, 1, 2, 244.00, 210, 210, 0, 3)",
    # Route 15: HYB -> BZA
    "(15, 7, 1, 0.00, 0, 0, 0, 1)",
    "(15, 25, 2, 313.00, 300, 300, 0, 6)",
    # Route 16: BZA -> HYB
    "(16, 25, 1, 0.00, 0, 0, 0, 6)",
    "(16, 7, 2, 313.00, 300, 300, 0, 1)",
    # Route 17: NDLS -> BSB
    "(17, 1, 1, 0.00, 0, 0, 0, 1)",
    "(17, 11, 2, 440.00, 270, 260, 10, 3)",
    "(17, 13, 3, 757.00, 480, 480, 0, 1)",
    # Route 18: BSB -> NDLS
    "(18, 13, 1, 0.00, 0, 0, 0, 1)",
    "(18, 11, 2, 317.00, 220, 210, 10, 2)",
    "(18, 1, 3, 757.00, 480, 480, 0, 1)"
)
[void]$sb.AppendLine(($stopsData -join ",`n") + ";`n")

# 5. SERVICES (22 services)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 5. SERVICES (22 records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO services (service_id, service_number, service_name, service_type, operating_days, is_active) VALUES")
$servicesData = @(
    "(1, '12951', 'Mumbai Tejas Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(2, '12952', 'New Delhi Tejas Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(3, '12301', 'Howrah Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(4, '12302', 'New Delhi Howrah Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(5, '12615', 'Grand Trunk Express', 'SUPERFAST', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(6, '12616', 'New Delhi GT Express', 'SUPERFAST', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(7, '20901', 'Mumbai - Ahmedabad Vande Bharat Express', 'VANDE_BHARAT', 'MON,TUE,WED,FRI,SAT,SUN', 1)",
    "(8, '20902', 'Ahmedabad - Mumbai Vande Bharat Express', 'VANDE_BHARAT', 'MON,TUE,WED,FRI,SAT,SUN', 1)",
    "(9, '20607', 'Chennai - Mysuru Vande Bharat Express', 'VANDE_BHARAT', 'MON,TUE,WED,FRI,SAT,SUN', 1)",
    "(10, '20608', 'Mysuru - Chennai Vande Bharat Express', 'VANDE_BHARAT', 'MON,TUE,WED,FRI,SAT,SUN', 1)",
    "(11, '12123', 'Deccan Queen Superfast Express', 'SUPERFAST', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(12, '12124', 'Pune Mumbai Deccan Queen', 'SUPERFAST', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(13, '12011', 'Kalka Shatabdi Express', 'SHATABDI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(14, '12012', 'New Delhi Shatabdi Express', 'SHATABDI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(15, '12795', 'Lingampalli - Vijayawada Intercity Express', 'INTERCITY', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(16, '12796', 'Vijayawada - Lingampalli Intercity Express', 'INTERCITY', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(17, '22436', 'New Delhi - Varanasi Vande Bharat Express', 'VANDE_BHARAT', 'TUE,WED,FRI,SAT,SUN', 1)",
    "(18, '22435', 'Varanasi - New Delhi Vande Bharat Express', 'VANDE_BHARAT', 'TUE,WED,FRI,SAT,SUN', 1)",
    "(19, '12953', 'August Kranti Tejas Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(20, '12954', 'NZM August Kranti Rajdhani Express', 'RAJDHANI', 'MON,TUE,WED,THU,FRI,SAT,SUN', 1)",
    "(21, '12245', 'Howrah - Yesvantpur Duronto Express', 'SUPERFAST', 'TUE,WED,FRI,SUN', 1)",
    "(22, '12246', 'Yesvantpur - Howrah Duronto Express', 'SUPERFAST', 'MON,THU,FRI,SUN', 1)"
)
[void]$sb.AppendLine(($servicesData -join ",`n") + ";`n")

# 6. VEHICLES (22 vehicles)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 6. VEHICLES (22 rakes)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO vehicles (vehicle_id, vehicle_number, vehicle_type, model_name, manufacture_year, total_coaches, total_capacity, maintenance_status) VALUES")
$vehiclesData = @()
for ($v = 1; $v -le 22; $v++) {
    $vType = if ($v -in @(7,8,9,10,17,18)) { "ELECTRIC_MULTIPLE_UNIT" } else { "LOCOMOTIVE_TRAIN" }
    $model = if ($v -in @(7,8,9,10,17,18)) { "Train-18 Vande Bharat Rake" } else { "LHB Tejas Coach Set" }
    $cap = 40 # 4 coaches x 10 seats
    $vehiclesData += "($v, 'RAKE-$($v.ToString('000'))', '$vType', '$model', 2022, 4, $cap, 'OPERATIONAL')"
}
[void]$sb.AppendLine(($vehiclesData -join ",`n") + ";`n")

# 7. SEATS (4 coaches per vehicle x 10 seats = 40 seats per vehicle, total 880 seats)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 7. SEATS (880 seat records across 22 vehicles)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO seats (seat_id, vehicle_id, coach_number, seat_number, seat_class, seat_type, fare_multiplier) VALUES")
$seatsData = @()
$seatIdCounter = 1
for ($v = 1; $v -le 22; $v++) {
    $coaches = @(
        @{Name="A1"; Class="2A"; Mult=1.80},
        @{Name="B1"; Class="3A"; Mult=1.40},
        @{Name="C1"; Class="CC"; Mult=1.20},
        @{Name="S1"; Class="SL"; Mult=1.00}
    )
    foreach ($c in $coaches) {
        for ($s = 1; $s -le 10; $s++) {
            $stype = @("LOWER", "MIDDLE", "UPPER", "SIDE_LOWER", "SIDE_UPPER", "WINDOW", "AISLE")[$s % 7]
            $seatsData += "($seatIdCounter, $v, '$($c.Name)', '$s', '$($c.Class)', '$stype', $($c.Mult))"
            $seatIdCounter++
        }
    }
}
[void]$sb.AppendLine(($seatsData -join ",`n") + ";`n")

# 8. TRIPS (120 trips scheduled across Oct, Nov, Dec 2026)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 8. TRIPS (120 scheduled trips)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO trips (trip_id, service_id, route_id, vehicle_id, trip_date, scheduled_departure, scheduled_arrival, actual_departure, actual_arrival, status, base_fare) VALUES")
$tripsData = @()
$startDate = [DateTime]::Parse("2026-10-01")
$tripIdCounter = 1
# Generate 120 trips across services 1..22 and routes 1..18
for ($t = 1; $t -le 120; $t++) {
    $servId = (($t - 1) % 22) + 1
    # Match route roughly to service
    $routeId = switch ($servId) {
        1 { 1 }
        2 { 2 }
        3 { 3 }
        4 { 4 }
        5 { 5 }
        6 { 6 }
        7 { 7 }
        8 { 8 }
        9 { 9 }
        10 { 10 }
        11 { 11 }
        12 { 12 }
        13 { 13 }
        14 { 14 }
        15 { 15 }
        16 { 16 }
        17 { 17 }
        18 { 18 }
        19 { 1 }
        20 { 2 }
        21 { 3 }
        22 { 4 }
        Default { 1 }
    }
    $vehId = $servId
    $tripDate = $startDate.AddDays([Math]::Floor($t / 2))
    $depTime = $tripDate.ToString("yyyy-MM-dd") + " 06:00:00"
    $arrTime = $tripDate.ToString("yyyy-MM-dd") + " 18:00:00"
    $status = if ($t -le 40) { "COMPLETED" } elseif ($t -eq 41) { "DELAYED" } else { "SCHEDULED" }
    $baseFare = 450.00 + ($routeId * 25.00)
    $tripsData += "($t, $servId, $routeId, $vehId, '$($tripDate.ToString("yyyy-MM-dd"))', '$depTime', '$arrTime', NULL, NULL, '$status', $baseFare)"
}
[void]$sb.AppendLine(($tripsData -join ",`n") + ";`n")

# 9. PASSENGERS (220 passengers)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 9. PASSENGERS (220 traveler profiles)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO passengers (passenger_id, user_id, first_name, last_name, gender, age, id_card_type, id_card_number, email, phone_number) VALUES")
$passengersData = @()
$firstNames = @("Aditya", "Aarav", "Rohan", "Kabir", "Vihaan", "Aanya", "Diya", "Isha", "Ananya", "Riya", "Manish", "Deepak", "Amit", "Rajesh", "Pooja", "Sangeeta", "Meenakshi", "Kavita", "Suresh", "Naresh")
$lastNames = @("Sharma", "Verma", "Gupta", "Patel", "Singh", "Reddy", "Nair", "Iyer", "Chopra", "Malhotra", "Banerjee", "Bose", "Mukherjee", "Das", "Joshi", "Kulkarni", "Deshmukh", "Pillai", "Yadav", "Pandey")
for ($p = 1; $p -le 220; $p++) {
    $fn = $firstNames[($p * 7) % $firstNames.Length]
    $ln = $lastNames[($p * 11) % $lastNames.Length]
    $gen = if ($p % 2 -eq 0) { "MALE" } else { "FEMALE" }
    $age = 18 + ($p % 60)
    $cardType = @("AADHAAR", "PASSPORT", "PAN", "VOTER_ID", "DRIVING_LICENSE")[$p % 5]
    $cardNum = "ID" + ($p * 83719 + 100000).ToString()
    $userIdVal = if ($p -le 25) { $p } else { (($p % 25) + 1) }
    $passengersData += "($p, $userIdVal, '$fn', '$ln', '$gen', $age, '$cardType', '$cardNum', 'p$p@gmail.com', '+91981100$($p.ToString('0000'))')"
}
[void]$sb.AppendLine(($passengersData -join ",`n") + ";`n")

# 10. BOOKINGS (550 bookings)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 10. BOOKINGS (550 reservation records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO bookings (booking_id, booking_reference, user_id, trip_id, booking_date, total_passengers, total_fare, booking_status) VALUES")
$bookingsData = @()
for ($b = 1; $b -le 550; $b++) {
    $pnr = "TM-" + ($b * 314159 % 90000000 + 10000000).ToString()
    $userId = (($b % 25) + 1)
    $tripId = (($b % 120) + 1)
    $bDate = $startDate.AddDays(($b % 60)).ToString("yyyy-MM-dd HH:mm:ss")
    $bStatus = if ($b -le 480) { "CONFIRMED" } elseif ($b -le 520) { "CANCELLED" } else { "WAITLISTED" }
    $fare = 650.00 + ($b % 15) * 50.00
    $bookingsData += "($b, '$pnr', $userId, $tripId, '$bDate', 1, $fare, '$bStatus')"
}
[void]$sb.AppendLine(($bookingsData -join ",`n") + ";`n")

# 11. TICKETS (550 tickets matching bookings)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 11. TICKETS (550 passenger tickets)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO tickets (ticket_id, booking_id, passenger_id, seat_id, origin_station_id, destination_station_id, ticket_number, fare_amount, ticket_status) VALUES")
$ticketsData = @()
for ($t = 1; $t -le 550; $t++) {
    $bId = $t
    $passengerId = (($t - 1) % 220) + 1
    # Assign seat from vehicle
    $sId = if ($t -gt 520) { "NULL" } else { (($t % 880) + 1).ToString() }
    $tktNum = "TKT-202610-" + ($t.ToString("0000"))
    $tktStatus = if ($t -le 480) { "CONFIRMED" } elseif ($t -le 520) { "CANCELLED" } else { "WAITLISTED" }
    $fare = 650.00 + ($t % 15) * 50.00
    $ticketsData += "($t, $bId, $passengerId, $sId, 1, 2, '$tktNum', $fare, '$tktStatus')"
}
[void]$sb.AppendLine(($ticketsData -join ",`n") + ";`n")

# 12. PAYMENTS (550 payments)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 12. PAYMENTS (550 settlement transactions)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO payments (payment_id, booking_id, transaction_reference, payment_method, amount, payment_status, paid_at) VALUES")
$paymentsData = @()
for ($pm = 1; $pm -le 550; $pm++) {
    $txnRef = "TXN-202610-" + ($pm.ToString("000000"))
    $method = @("UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET")[$pm % 5]
    $fare = 650.00 + ($pm % 15) * 50.00
    $status = if ($pm -le 480) { "SUCCESS" } elseif ($pm -le 520) { "REFUNDED" } else { "SUCCESS" }
    $pDate = $startDate.AddDays(($pm % 60)).ToString("yyyy-MM-dd HH:mm:ss")
    $paymentsData += "($pm, $pm, '$txnRef', '$method', $fare, '$status', '$pDate')"
}
[void]$sb.AppendLine(($paymentsData -join ",`n") + ";`n")

# 13. CANCELLATIONS (40 cancellations for tickets 481..520)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 13. CANCELLATIONS (40 refund records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO cancellations (cancellation_id, booking_id, ticket_id, cancellation_reason, cancellation_fee, refund_amount, refund_status, cancelled_at) VALUES")
$cancelsData = @()
for ($c = 1; $c -le 40; $c++) {
    $tktId = 480 + $c
    $bId = $tktId
    $fare = 650.00 + ($tktId % 15) * 50.00
    $fee = [Math]::Round($fare * 0.15, 2)
    $refund = [Math]::Round($fare - $fee, 2)
    $reason = @("Personal emergency", "Change of travel plans", "Business trip rescheduled", "Flight booked instead")[$c % 4]
    $cDate = $startDate.AddDays(($c + 5)).ToString("yyyy-MM-dd 14:00:00")
    $cancelsData += "($c, $bId, $tktId, '$reason', $fee, $refund, 'PROCESSED', '$cDate')"
}
[void]$sb.AppendLine(($cancelsData -join ",`n") + ";`n")

# 14. WAITLISTS (30 waitlist queue items)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 14. WAITLISTS (30 queue entries)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO waitlists (waitlist_id, trip_id, passenger_id, booking_id, seat_class, waitlist_number, status) VALUES")
$waitlistsData = @()
for ($w = 1; $w -le 30; $w++) {
    $bId = 520 + $w
    $passengerId = (($bId - 1) % 220) + 1
    $tripId = (($bId % 120) + 1)
    $wClass = @("2A", "3A", "CC", "SL")[$w % 4]
    $waitlistsData += "($w, $tripId, $passengerId, $bId, '$wClass', $w, 'WAITING')"
}
[void]$sb.AppendLine(($waitlistsData -join ",`n") + ";`n")

# 15. DELAYS (60 operational delay records)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 15. DELAYS (60 operational incident records)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO delays (delay_id, trip_id, station_id, delay_minutes, delay_reason, remarks, recorded_at) VALUES")
$delaysData = @()
$reasons = @("WEATHER", "TRACK_MAINTENANCE", "SIGNAL_FAILURE", "CONGESTION", "TECHNICAL_GLITCH")
for ($d = 1; $d -le 60; $d++) {
    $tripId = (($d * 2) % 120) + 1
    $stId = (($d * 3) % 35) + 1
    $mins = 10 + ($d * 5 % 75)
    $rsn = $reasons[$d % $reasons.Length]
    $rem = "Operational delay recorded due to " + $rsn.ToLower().Replace("_", " ")
    $dDate = $startDate.AddDays(($d % 40)).ToString("yyyy-MM-dd 10:30:00")
    $delaysData += "($d, $tripId, $stId, $mins, '$rsn', '$rem', '$dDate')"
}
[void]$sb.AppendLine(($delaysData -join ",`n") + ";`n")

# 16. DEMAND PREDICTIONS (50 ML predictions)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 16. DEMAND PREDICTIONS (50 machine learning predictions)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO demand_predictions (prediction_id, route_id, prediction_date, predicted_passenger_demand, confidence_lower_bound, confidence_upper_bound, model_name, model_version) VALUES")
$predsData = @()
for ($pr = 1; $pr -le 50; $pr++) {
    $rId = (($pr % 18) + 1)
    $pDate = $startDate.AddDays(70 + $pr).ToString("yyyy-MM-dd")
    $demand = 350 + ($pr * 7 % 180)
    $low = $demand - 35
    $high = $demand + 40
    $predsData += "($pr, $rId, '$pDate', $demand, $low, $high, 'RandomForestRegressor', 'v1.0')"
}
[void]$sb.AppendLine(($predsData -join ",`n") + ";`n")

# 17. AUDIT LOGS (80 audit entries)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 17. AUDIT LOGS (80 historical compliance log entries)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by, changed_at) VALUES")
$auditData = @()
for ($a = 1; $a -le 80; $a++) {
    $oldVal = "{`"status`": `"PENDING`"}"
    $newVal = "{`"status`": `"CONFIRMED`"}"
    $auditData += "('bookings', '$a', 'UPDATE', '$oldVal', '$newVal', 'SYSTEM', '2026-10-15 12:00:00')"
}
[void]$sb.AppendLine(($auditData -join ",`n") + ";`n")

# 18. TRIP SEAT INVENTORY (Populate for trips 1..10 with their vehicle seats)
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("-- 18. TRIP SEAT INVENTORY (Granular seat availability for trips)")
[void]$sb.AppendLine("-- -----------------------------------------------------------------------------")
[void]$sb.AppendLine("INSERT INTO trip_seat_inventory (trip_id, seat_id, is_available, reserved_at, held_until, lock_version)")
[void]$sb.AppendLine("SELECT ")
[void]$sb.AppendLine("    tr.trip_id,")
[void]$sb.AppendLine("    st.seat_id,")
[void]$sb.AppendLine("    CASE WHEN MOD(tr.trip_id + st.seat_id, 3) = 0 THEN FALSE ELSE TRUE END AS is_available,")
[void]$sb.AppendLine("    CASE WHEN MOD(tr.trip_id + st.seat_id, 3) = 0 THEN tr.created_at ELSE NULL END AS reserved_at,")
[void]$sb.AppendLine("    NULL AS held_until,")
[void]$sb.AppendLine("    0 AS lock_version")
[void]$sb.AppendLine("FROM trips tr")
[void]$sb.AppendLine("JOIN seats st ON tr.vehicle_id = st.vehicle_id;")
[void]$sb.AppendLine()
[void]$sb.AppendLine("SET FOREIGN_KEY_CHECKS = 1;")

$content = $sb.ToString()
[System.IO.File]::WriteAllText("c:\Users\NAGARJUNA\Desktop\transitmatrix\database\seed.sql", $content)
[System.IO.File]::WriteAllText("c:\Users\NAGARJUNA\Desktop\transitmatrix\database\migrations\V5__sample_seed_data.sql", $content)
Write-Output "Successfully generated seed.sql and V5__sample_seed_data.sql! Total characters: $($content.Length)"
