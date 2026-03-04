# 📸 Visual Guide - What Each Page Looks Like

## 🏠 Landing Page (/)

### Hero Section
```
┌─────────────────────────────────────────────────────────┐
│  ⚡ KenGen Tender Tracking                    [Navbar]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ⚡ Tender Tracking System                             │
│   Streamline your procurement process with our          │
│   comprehensive tender management solution.              │
│                                                          │
│   [📄 View All Tenders]  [📊 Dashboard]                 │
└─────────────────────────────────────────────────────────┘
```

### Statistics Cards
```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ 📄 150     │  │ ⏳ 45      │  │ 👥 120     │  │ 💰 500M    │
│ Total      │  │ Active     │  │ Active     │  │ Total      │
│ Tenders    │  │ Tenders    │  │ Employees  │  │ Value      │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

### Key Features (3 columns)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   🔍 Search     │  │   📊 Analytics  │  │   👥 Committees │
│   Advanced      │  │   Reporting     │  │   Management    │
│   Search &      │  │   Get insights  │  │   Manage        │
│   Filters       │  │   with charts   │  │   committees    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Recent Tenders
```
┌─────────────────────────────────────────────────────────┐
│  Recent Tenders                      [View All →]       │
├─────────────────────────────────────────────────────────┤
│  Tender ID: 38                                          │
│  Design and Supply of Stator Coils...                  │
│  🗺️ Eastern  🏢 Operations  📋 Tender                   │
│                                    Closes: 25 Oct 2025  │
├─────────────────────────────────────────────────────────┤
│  [More tenders...]                                      │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Dashboard (/dashboard/)

### Analytics Cards
```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ 📊 LOA     │  │ 📄 Contract│  │ 📅 Upcoming│  │ ⚡ Recent  │
│ Status     │  │ Status     │  │ (30 days)  │  │ Activity   │
│ Count: 5   │  │ Count: 4   │  │ Count: 12  │  │ Count: 10  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

### Main Content (2 columns)
```
Left Column (8/12):                Right Column (4/12):
┌─────────────────────────┐       ┌──────────────────┐
│ 🗺️ Tenders by Region    │       │ 📋 Procurement   │
│ ─────────────────────    │       │    Types         │
│ Eastern    [25] ████████ │       │ ──────────────   │
│ Western    [15] █████    │       │ Tender      (50) │
│ Central    [10] ███      │       │ RFQ         (30) │
└─────────────────────────┘       │ Direct      (20) │
                                   └──────────────────┘
┌─────────────────────────┐       ┌──────────────────┐
│ 🏢 Top Departments      │       │ ✅ e-Contract Step    │
│ ─────────────────────    │       │ ──────────────   │
│ Operations [30] ████████ │       │ Draft       (25) │
│ Finance    [20] █████    │       │ Approved    (15) │
└─────────────────────────┘       │ Pending     (10) │
                                   └──────────────────┘
┌─────────────────────────┐       ┌──────────────────┐
│ ⏱️ Recent Tenders       │       │ 📅 Upcoming      │
│ ─────────────────────    │       │    Closings      │
│ Tender 38              │       │ ──────────────   │
│ Generator rewinding... │       │ T-42  Dec 20     │
│ 👤 John Doe            │       │ T-55  Dec 25     │
│ ─────────────────────    │       │ T-67  Dec 30     │
│ [More...]              │       └──────────────────┘
└─────────────────────────┘
```

---

## 📋 Tender List (/tenders/)

### Filters Section
```
┌─────────────────────────────────────────────────────────┐
│  🔍 Search: [____________]  🗺️ Region: [All ▼]         │
│  🏢 Dept: [All ▼]  📋 Type: [All ▼]  ✅ Status: [All ▼] │
│  [Apply Filters]  [Clear Filters]                       │
└─────────────────────────────────────────────────────────┘
```

### Tender Cards
```
┌─────────────────────────────────────────────────────────┐
│  Tender ID : 38                                         │
│  Design and Supply of Stator Coils, Installation,      │
│  Rewinding, Testing and Commissioning of Unit 1...     │
│                                                          │
│  🗺️ Eastern  🏢 Operations  🏭 Sondu  📋 Tender         │
│  👤 Created by: Valary Chelagat                         │
│  #️⃣ eGP: KENGEN/197/0001/2025-26                        │
│                                                          │
│                                  LOA: ✅ Draft, L        │
│                                  Contract: 📄 Draft     │
│                                  📅 Advert: 09 Sep 2025 │
│                                  📅 Closes: 25 Oct 2025 │
│                                  💰 KSh 150,000,000.00  │
│                                  [View Details →]       │
└─────────────────────────────────────────────────────────┘
```

---

## 📄 Tender Detail (/tenders/38/)

### Header
```
┌─────────────────────────────────────────────────────────┐
│  Home > Tenders > Tender ID : 38                        │
├─────────────────────────────────────────────────────────┤
│  Tender ID : 38                          [✏️ Edit]      │
│  🗺️ Eastern  🏢 Operations  📋 Tender                   │
└─────────────────────────────────────────────────────────┘
```

### Content (2 columns)
```
Main Content (8/12):              Sidebar (4/12):
┌──────────────────────────┐     ┌─────────────────┐
│ 📄 Tender Description    │     │ 🚩 Status       │
│ ────────────────────      │     │ ───────────     │
│ Design and Supply of     │     │ e-Contract Step:     │
│ Stator Coils, Install... │     │ ✅ Draft, L     │
└──────────────────────────┘     │ Contract:       │
                                  │ 📄 Draft        │
┌──────────────────────────┐     └─────────────────┘
│ #️⃣ References & IDs      │     
│ ────────────────────      │     ┌─────────────────┐
│ eGP: KENGEN/197/...      │     │ 💰 Financial    │
│ KenGen: KGN-SONDU...     │     │ ───────────     │
│ Requisition: EPS/382...  │     │ Est. Value:     │
└──────────────────────────┘     │ KSh 150,000,000 │
                                  └─────────────────┘
┌──────────────────────────┐     
│ 📅 Timeline & Dates      │     ┌─────────────────┐
│ ────────────────────      │     │ 🏢 Organization │
│ Advert: 9 Sep 2025      │     │ ───────────     │
│ Closing: 25 Oct 2025    │     │ Region: Eastern │
│ Time: 10:00 AM          │     │ Dept: Operations│
│ Validity: [Date]        │     │ Section: Sondu  │
└──────────────────────────┘     └─────────────────┘

┌──────────────┐  ┌──────────────┐  ┌─────────────────┐
│ 👥 Opening   │  │ 👥 Evaluation│  │ 👤 Personnel    │
│    Committee │  │    Committee │  │ ───────────     │
│ ──────────── │  │ ──────────── │  │ Creator:        │
│ John Doe     │  │ Jane Smith   │  │ Valary Chelagat │
│ Chair        │  │ Lead         │  │                 │
│ Mary Kim     │  │ Tom Brown    │  │ Contract:       │
│ Member       │  │ Evaluator    │  │ W. Nyangweso    │
└──────────────┘  └──────────────┘  └─────────────────┘
```

---

## 👥 Employee Directory (/employees/)

### Filters
```
┌─────────────────────────────────────────────────────────┐
│  🔍 Search: [____________]  🏢 Department: [All ▼]      │
│  [Filter]                                                │
└─────────────────────────────────────────────────────────┘
```

### Employee Table
```
┌─────────────────────────────────────────────────────────┐
│ ID    │ Name           │ Email          │ Dept    │ ... │
├───────┼────────────────┼────────────────┼─────────┼─────┤
│ E001  │ 👤 John Doe    │ john@ken...    │ Ops     │ ✏️  │
│ E002  │ 👤 Jane Smith  │ jane@ken...    │ Finance │ ✏️  │
│ E003  │ 👤 Mary Kim    │ mary@ken...    │ Eng     │ ✏️  │
└───────┴────────────────┴────────────────┴─────────┴─────┘
```

### Statistics
```
┌────────────┐  ┌────────────┐  ┌────────────┐
│ 👥 120     │  │ 🏢 15      │  │ 💼 120     │
│ Total      │  │ Depts      │  │ Active     │
│ Employees  │  │            │  │ Staff      │
└────────────┘  └────────────┘  └────────────┘
```

---

## 🎨 Design Elements Used

### Color Coding
- **Blue** (Primary) - Main actions, primary info
- **Green** (Success) - Active, approved, success states
- **Yellow** (Warning) - Pending, warnings, attention needed
- **Red** (Danger) - Errors, critical items
- **Gray** (Secondary) - Supporting information

### Icons
- 📄 Tenders/Documents
- 👥 People/Committees
- 🗺️ Regions
- 🏢 Departments/Buildings
- 📊 Statistics/Analytics
- 📅 Dates/Calendar
- 💰 Financial/Money
- ✅ Status/Approved
- 🔍 Search
- ✏️ Edit

### Components
- Cards with shadows
- Badges for statuses
- Progress bars
- Tables with hover
- Buttons with icons
- Search bars
- Dropdown filters
- Breadcrumbs
- Avatar circles

### Responsive Breakpoints
- Mobile: < 768px (Stack vertically)
- Tablet: 768px - 1024px (2 columns)
- Desktop: > 1024px (Full layout)

---

## 🚀 Navigation Flow

```
Main Navigation Bar (Always visible):
[🏠 Home] [📊 Dashboard] [📄 Tenders] [👥 Employees] [⚙️ Admin]

Footer Links:
- Dashboard
- All Tenders  
- Employees
- Admin Panel

Quick Actions:
- View All Tenders (Landing → List)
- View Details (List → Detail)
- Edit (Detail → Admin)
- Add New (List → Admin)
```

This visual guide shows you exactly what to expect when you visit each page of your tender tracking system!
