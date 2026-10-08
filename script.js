/**
 * TruthTag Intelligence — Product Authenticity & Provenance Intelligence Platform
 * Master JavaScript Engine
 * Architecture:
 * - Local Database & Telemetry Engine (TruthTagDB)
 * - Verification & Consistency Inspector Engine (TruthTagVerifier)
 * - TruthGraph™ Interactive Relational Map Renderer
 * - 21st.dev UI/UX Patterns:
 *   1. Immersive Animated Hero & Telemetry Stream
 *   2. Cursor-Following Spotlight & Magnetic Controls
 *   3. Global Command Palette (Cmd+K / Ctrl+K)
 *   4. Bento-Grid Intelligence Dashboard (Dynamic metrics & charts)
 *   5. Interactive Protocol Timeline
 * - Product Registration Studio (Multi-Step Wizard)
 * - Optical Scanner & Image Ingestion Viewport
 * - Audit History Manager & Executive Report Generator
 */

'use strict';

/* ==========================================================================
   1. Initial Authenticity Dataset (Realistic Fictional Ledger Records)
   ========================================================================== */
const INITIAL_INTELLIGENCE_LEDGER = [
  {
    id: 'ledger-001',
    name: 'AuraSound Apex Pro Wireless ANC Headphones',
    brand: 'AuraSound Labs',
    category: 'Electronics',
    productId: 'AUD-9921-X',
    batch: 'B24-8891',
    serial: 'SN-772109',
    status: 'match',
    facility: 'AuraSound UK Engineering Facility, Oxford, UK',
    productionDate: 'August 14, 2025',
    authorizedChannels: 'AuraSound Direct, BestBuy, Currys UK, B&H Photo',
    securityFeature: 'Holographic Void Seal & Micro-Engraved QR Matrix',
    notes: 'Look for rainbow holographic sheen on inner seal and embossed serial tag on headband.',
    recordDigest: 'SHA256: 9a7f8d1c028e3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a',
    reason: 'Official Brand Ledger Match: The submitted identifier matches an authorized manufacturing run registered by AuraSound Labs with zero active counterfeit alerts.'
  },
  {
    id: 'ledger-002',
    name: 'Vitalis Botanical Glow Facial Serum',
    brand: 'Vitalis Laboratories',
    category: 'Skincare',
    productId: 'VTL-402',
    batch: 'LOT-2024-09',
    serial: 'SN-55412',
    status: 'match',
    facility: 'Vitalis Clean Cosmetics Facility, Provence, France',
    productionDate: 'September 22, 2025',
    authorizedChannels: 'Vitalis Paris Flagship, Sephora, Nordstrom, Mecca',
    securityFeature: 'Tamper-Evident Breakaway Foil & Lot Stamp on Glass Base',
    notes: 'Authentic bottles have lot code screen-printed in white ink on the base of the glass bottle.',
    recordDigest: 'SHA256: 3c8b1a4f7e2d9c0b5f6a8e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b',
    reason: 'Active Cosmetic Batch Registration: Authenticated batch record for LOT-2024-09 confirmed with verified laboratory batch release certificate.'
  },
  {
    id: 'ledger-003',
    name: 'AeroStride Velocity Carbon Running Shoes',
    brand: 'AeroStride',
    category: 'Footwear',
    productId: 'AERO-900',
    batch: 'B-7712',
    serial: 'SN-33901',
    status: 'match',
    facility: 'AeroStride Technical Footwear Plant, Busan, South Korea',
    productionDate: 'January 10, 2026',
    authorizedChannels: 'AeroStride Global, Fleet Feet, Dick’s Sporting Goods',
    securityFeature: 'Encrypted NFC Tongue Tag & Embedded RFID Thread',
    notes: 'Inner tongue tag features high-density woven label with crisp vector typography.',
    recordDigest: 'SHA256: 7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c',
    reason: 'Verified Production Record: The model SKU and serial sequence match verified production allocations with authorized distributor records.'
  },
  {
    id: 'ledger-004',
    name: 'NordicShield Extreme Weather Down Parka',
    brand: 'NordicShield Outerwear',
    category: 'Apparel',
    productId: 'NS-8800',
    batch: 'BATCH-FLAGGED-01',
    serial: 'SN-66601',
    status: 'warning',
    facility: 'NordicShield Arctic Wear Ltd, Oslo, Norway',
    productionDate: 'Unverified / Flagged Counterfeit Series',
    authorizedChannels: 'Unauthorized Gray-Market Sellers & Fake Pop-Up Stores',
    securityFeature: 'Suspected Counterfeit Cloned Hangtag',
    notes: 'Counterfeiters have duplicated this hangtag barcode across hundreds of non-insulated garments.',
    recordDigest: 'SHA256: 4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b',
    reason: '🚨 HIGH RISK COUNTERFEIT WARNING: Identifier is linked to a widely reported counterfeit batch. Unlicensed factories have replicated this tag on low-grade synthetic garments with synthetic fill, posing severe hypothermia risks in sub-zero conditions.'
  },
  {
    id: 'ledger-005',
    name: 'OmniCharge MagSafe 100W Power Bank',
    brand: 'OmniPower Global',
    category: 'Electronics',
    productId: 'OP-100W',
    batch: 'B-990-REC',
    serial: 'SN-10901',
    status: 'warning',
    facility: 'OmniPower Hardware Labs, Taipei, Taiwan',
    productionDate: 'May 04, 2025 (Recalled Series)',
    authorizedChannels: 'Recall Notice: Authorization Revoked Globally',
    securityFeature: 'Cloned Safety Certification Logo',
    notes: 'Units with batch B-990-REC or duplicate serial SN-10901 are subject to official safety recall due to cell degradation risks.',
    recordDigest: 'SHA256: 1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e',
    reason: '⚠️ SAFETY RECALL & DUPLICATION ALERT: Batch B-990-REC is officially flagged on the TruthTag safety ledger. In addition, our automated anomaly engine has detected over 420 duplicate queries for serial SN-10901, indicating unauthorized serial cloning.'
  },
  {
    id: 'ledger-006',
    name: 'Chronos Heritage Automatic Diver Watch',
    brand: 'Chronos Horology',
    category: 'Luxury',
    productId: 'CRN-3301',
    batch: 'BATCH-CH-44',
    serial: 'SN-88203',
    status: 'match',
    facility: 'Chronos Atelier, Geneva, Switzerland',
    productionDate: 'November 05, 2025',
    authorizedChannels: 'Chronos Boutiques, Watches of Switzerland, Bucherer',
    securityFeature: 'Laser-Etched Caseback Serial & Cryptographic Sapphire Card',
    notes: 'Laser engraving on caseback has 0.15mm depth with certified Swiss chronometer seal.',
    recordDigest: 'SHA256: 8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b',
    reason: 'Official Master Horology Ledger Entry: Serial number matches verified single-unit registration record in the Geneva brand ledger.'
  }
];

/* ==========================================================================
   2. Local Database & Telemetry Service (TruthTagDB)
   ========================================================================== */
const STORAGE_KEYS = {
  CUSTOM_RECORDS: 'truthtag_custom_records_v3',
  AUDIT_HISTORY: 'truthtag_investigation_history_v3'
};

class TruthTagDB {
  static getCustomRecords() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CUSTOM_RECORDS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error reading custom records from localStorage', e);
      return [];
    }
  }

  static saveCustomRecord(record) {
    try {
      const current = this.getCustomRecords();
      current.unshift(record);
      localStorage.setItem(STORAGE_KEYS.CUSTOM_RECORDS, JSON.stringify(current));
      return true;
    } catch (e) {
      console.error('Error saving custom record', e);
      return false;
    }
  }

  static getAllRecords() {
    const custom = this.getCustomRecords();
    return [...custom, ...INITIAL_INTELLIGENCE_LEDGER];
  }

  static getHistory() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.AUDIT_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error reading audit history', e);
      return [];
    }
  }

  static addHistory(record) {
    try {
      const history = this.getHistory();
      history.unshift(record);
      const trimmed = history.slice(0, 60);
      localStorage.setItem(STORAGE_KEYS.AUDIT_HISTORY, JSON.stringify(trimmed));
      return true;
    } catch (e) {
      console.error('Error saving audit history', e);
      return false;
    }
  }

  static clearHistory() {
    try {
      localStorage.removeItem(STORAGE_KEYS.AUDIT_HISTORY);
      return true;
    } catch (e) {
      console.error('Error clearing audit history', e);
      return false;
    }
  }

  static deleteHistoryItem(id) {
    try {
      const history = this.getHistory();
      const updated = history.filter(item => item.id !== id);
      localStorage.setItem(STORAGE_KEYS.AUDIT_HISTORY, JSON.stringify(updated));
      return true;
    } catch (e) {
      console.error('Error deleting history item', e);
      return false;
    }
  }
}

/* ==========================================================================
   3. Verification & Consistency Inspector Engine
   ========================================================================== */
class TruthTagVerifier {
  static cleanString(str) {
    if (!str) return '';
    return str.toString().trim().toLowerCase().replace(/[\s\-_]/g, '');
  }

  /**
   * Run verification check against local ledger
   */
  static verify(rawQuery) {
    const allRecords = TruthTagDB.getAllRecords();
    const query = typeof rawQuery === 'object' ? (rawQuery.singleQuery || rawQuery.productId || '') : rawQuery;
    const cleanQ = this.cleanString(query);

    if (!cleanQ) return null;

    // Direct match search order: Serial -> ProductId/SKU -> Batch -> Substring in Brand/Name
    let match = allRecords.find(item => this.cleanString(item.serial) === cleanQ);
    let matchField = 'Unique Unit Serial Number';

    if (!match) {
      match = allRecords.find(item => this.cleanString(item.productId) === cleanQ);
      matchField = 'Model SKU / Product ID';
    }

    if (!match) {
      match = allRecords.find(item => this.cleanString(item.batch) === cleanQ);
      matchField = 'Manufacturing Batch / Lot Code';
    }

    if (!match) {
      match = allRecords.find(item => 
        this.cleanString(item.name).includes(cleanQ) || 
        cleanQ.includes(this.cleanString(item.name)) ||
        this.cleanString(item.brand).includes(cleanQ)
      );
      matchField = 'Brand / Product Catalog Lookup';
    }

    const auditId = 'TRUTH-' + new Date().getFullYear() + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    const timestamp = new Date().toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });

    if (match) {
      const isWarning = match.status === 'warning';
      return {
        id: 'audit-' + Date.now(),
        auditId: auditId,
        timestamp: timestamp,
        status: isWarning ? 'warning' : 'match',
        statusTitle: isWarning ? 'Potential Inconsistency' : 'Record Match Found',
        productName: match.name,
        brand: match.brand,
        category: match.category,
        productId: match.productId,
        batch: match.batch,
        serial: match.serial,
        submittedQuery: query,
        matchField: matchField,
        facility: match.facility,
        productionDate: match.productionDate,
        authorizedChannels: match.authorizedChannels,
        securityFeature: match.securityFeature,
        notes: match.notes,
        recordDigest: match.recordDigest || ('SHA256: ' + Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2)),
        reason: match.reason,
        // Field-by-field consistency matrix
        consistencyMatrix: [
          { field: 'Product Name', submitted: query.includes(match.name) ? match.name : 'Identifier Query', registered: match.name, status: 'match', note: 'Product commercial title aligned with manufacturer registry.' },
          { field: 'Brand Entity', submitted: match.brand, registered: match.brand, status: 'match', note: 'Accredited brand authority signature verified.' },
          { field: 'Product SKU', submitted: match.productId, registered: match.productId, status: 'match', note: 'Model identifier matches authorized product specifications.' },
          { field: 'Batch / Lot Code', submitted: match.batch, registered: match.batch, status: isWarning ? 'conflict' : 'match', note: isWarning ? 'CRITICAL: Batch code has active counterfeit clone alert.' : 'Lot sequence valid and uncompromised.' },
          { field: 'Serial Sequence', submitted: match.serial, registered: match.serial, status: isWarning ? 'conflict' : 'match', note: isWarning ? 'Serial number flagged for duplicate anomaly scans.' : 'Serial mathematically fits registered factory allocation.' }
        ]
      };
    }

    // Inconclusive outcome
    return {
      id: 'audit-' + Date.now(),
      auditId: auditId,
      timestamp: timestamp,
      status: 'inconclusive',
      statusTitle: 'Inconclusive',
      productName: 'Unregistered Identifier',
      brand: 'Unlisted Entity',
      category: 'Unverified Category',
      productId: 'Not Found in Registry',
      batch: 'Not Found in Registry',
      serial: 'Not Found in Registry',
      submittedQuery: query,
      matchField: 'No Matching Cryptographic Hash Found',
      facility: 'Unknown / Unverified Facility',
      productionDate: 'No Verified Records Available',
      authorizedChannels: 'Cannot confirm legitimate retail channels',
      securityFeature: 'Unknown / Unspecified Profile',
      notes: 'No packaging security specification available for this identifier.',
      recordDigest: 'NO_RECORD_DIGEST',
      reason: 'Identifier Not Found in Active Ledger: The submitted identifier could not be matched against any registered brand authority records in TruthTag. This frequently occurs with unauthorized duplicates, regional variants not enrolled in this ledger, or typographical errors.',
      consistencyMatrix: [
        { field: 'Product Name', submitted: query, registered: 'Not Registered', status: 'missing', note: 'No matching product title in active ledger.' },
        { field: 'Brand Entity', submitted: 'Unknown', registered: 'Unlisted', status: 'missing', note: 'Authority signature absent from trust anchors.' },
        { field: 'Product SKU', submitted: query, registered: 'Not Registered', status: 'missing', note: 'SKU absent from participating manufacturer registries.' },
        { field: 'Batch / Lot Code', submitted: 'Unspecified', registered: 'Unlisted', status: 'missing', note: 'Batch record not found.' },
        { field: 'Serial Sequence', submitted: 'Unspecified', registered: 'Unlisted', status: 'missing', note: 'Unit sequence not registered.' }
      ]
    };
  }
}

/* ==========================================================================
   4. Application Controller & UI Management (TruthTagApp)
   ========================================================================== */
class TruthTagApp {
  constructor() {
    this.currentInvestigation = null;
    this.historyFilter = 'all';
    this.historySearch = '';
    this.catalogFilter = 'all';
    this.catalogSearch = '';
    this.webcamStream = null;
    this.activeWizardStep = 1;
    this.wizardData = {};

    this.cacheDOMElements();
    this.initSpotlight();
    this.initCommandPalette();
    this.bindEvents();
    this.renderBentoDashboard();
    this.renderCatalog();
    this.renderHistory();
    this.initTruthGraphPreview();
    this.initYear();
  }

  cacheDOMElements() {
    // Navigation
    this.header = document.getElementById('site-header');
    this.mobileToggle = document.getElementById('mobile-toggle');
    this.mobileDrawer = document.getElementById('mobile-drawer');
    this.headerScannerBtn = document.getElementById('header-scanner-btn');
    this.mobileScannerTrigger = document.getElementById('mobile-scanner-trigger');

    // Hero Form
    this.heroForm = document.getElementById('hero-verify-form');
    this.heroInput = document.getElementById('hero-query-input');
    this.heroValidationRow = document.getElementById('hero-validation-row');
    this.heroValidationMsg = document.getElementById('hero-validation-msg');
    this.heroQuickChips = document.querySelectorAll('.quick-chip');
    this.heroLogStream = document.getElementById('hero-log-stream');

    // Dossier & Investigation Workspace
    this.loader = document.getElementById('investigation-loader');
    this.loaderFill = document.getElementById('loader-progress-fill');
    this.loaderMainMsg = document.getElementById('loader-main-message');
    this.loaderSubMsg = document.getElementById('loader-sub-message');
    this.termPill1 = document.getElementById('term-pill-1');
    this.termPill2 = document.getElementById('term-pill-2');
    this.termPill3 = document.getElementById('term-pill-3');

    this.dossierWrapper = document.getElementById('investigation-dossier');
    this.dossierHeader = document.getElementById('dossier-header');
    this.dossierTabs = document.querySelectorAll('.dossier-tab');
    this.dossierPanels = document.querySelectorAll('.dossier-tab-content');
    this.inspectorTableBody = document.getElementById('inspector-table-body');
    this.inspectorScoreBadge = document.getElementById('inspector-score-badge');
    this.truthgraphSvg = document.getElementById('truthgraph-svg');
    this.nodeInspectorText = document.getElementById('node-inspector-text');
    this.physicalGuideContainer = document.getElementById('physical-guide-container');

    // Dossier Action Buttons
    this.btnPrintDossier = document.getElementById('btn-print-dossier');
    this.btnCopyDossierLink = document.getElementById('btn-copy-dossier-link');
    this.btnNewInvestigation = document.getElementById('btn-new-investigation');

    // Bento Dashboard Elements
    this.bentoTotalChecks = document.getElementById('bento-total-checks');
    this.bentoMatchedCount = document.getElementById('bento-matched-count');
    this.bentoInconclusiveCount = document.getElementById('bento-inconclusive-count');
    this.bentoWarningCount = document.getElementById('bento-warning-count');
    this.bentoLedgerCapacity = document.getElementById('bento-ledger-capacity');
    this.bentoStreamList = document.getElementById('bento-stream-list');
    this.bentoCategoryBars = document.getElementById('bento-category-bars');
    this.donutSegMatch = document.getElementById('donut-seg-match');
    this.donutSegWarning = document.getElementById('donut-seg-warning');
    this.donutSegInconclusive = document.getElementById('donut-seg-inconclusive');
    this.donutCenterRate = document.getElementById('donut-center-rate');

    // Bento Action Buttons
    this.tileOpenScanner = document.getElementById('tile-open-scanner');
    this.tileRegisterProduct = document.getElementById('tile-register-product');
    this.tileExportAudit = document.getElementById('tile-export-audit');
    this.tileOpenCmd = document.getElementById('tile-open-cmd');

    // Catalog & Records Explorer
    this.catalogGrid = document.getElementById('catalog-cards-grid');
    this.catalogSearchInput = document.getElementById('catalog-search-input');
    this.catalogPills = document.querySelectorAll('#category-filter-group .cat-pill');
    this.catalogEmptyState = document.getElementById('catalog-empty-state');

    // Protocol Timeline
    this.timelineCards = document.querySelectorAll('.timeline-step-card');

    // Registration Studio (Wizard)
    this.studioForm = document.getElementById('studio-registration-form');
    this.wizPanes = [
      document.getElementById('wizard-pane-1'),
      document.getElementById('wizard-pane-2'),
      document.getElementById('wizard-pane-3'),
      document.getElementById('wizard-pane-4')
    ];
    this.wizPills = [
      document.getElementById('wiz-step-pill-1'),
      document.getElementById('wiz-step-pill-2'),
      document.getElementById('wiz-step-pill-3'),
      document.getElementById('wiz-step-pill-4')
    ];
    this.wizNext1 = document.getElementById('wiz-next-1');
    this.wizPrev2 = document.getElementById('wiz-prev-2');
    this.wizNext2 = document.getElementById('wiz-next-2');
    this.wizPrev3 = document.getElementById('wiz-prev-3');
    this.wizNext3 = document.getElementById('wiz-next-3');
    this.wizPrev4 = document.getElementById('wiz-prev-4');
    this.studioReviewSummary = document.getElementById('studio-review-summary');

    // History
    this.historyList = document.getElementById('history-items-list');
    this.historyEmptyView = document.getElementById('history-empty-view');
    this.historyFilterPills = document.querySelectorAll('#history-filter-pills .h-pill');
    this.historySearchField = document.getElementById('history-search-field');
    this.histExportBtn = document.getElementById('hist-export-btn');
    this.histClearBtn = document.getElementById('hist-clear-btn');
    this.hCountAll = document.getElementById('h-count-all');
    this.hCountMatch = document.getElementById('h-count-match');
    this.hCountInconclusive = document.getElementById('h-count-inconclusive');
    this.hCountWarning = document.getElementById('h-count-warning');

    // Scanner Modal
    this.scannerModal = document.getElementById('scanner-modal');
    this.scannerModalClose = document.getElementById('scanner-modal-close');
    this.modalWebcamVideo = document.getElementById('modal-webcam-video');
    this.modalScannerIdle = document.getElementById('modal-scanner-idle');
    this.modalCameraToggleBtn = document.getElementById('modal-camera-toggle-btn');
    this.modalQrFile = document.getElementById('modal-qr-file');
    this.scannerPresetBtns = document.querySelectorAll('.scanner-preset-btn');

    // Command Palette
    this.cmdPalette = document.getElementById('cmd-palette');
    this.cmdKTrigger = document.getElementById('cmd-k-trigger');
    this.cmdSearchInput = document.getElementById('cmd-search-input');
    this.cmdCloseBtn = document.getElementById('cmd-close-btn');
    this.cmdResultsList = document.getElementById('cmd-results-list');

    // FAQs & Contact
    this.faqItems = document.querySelectorAll('.faq-item');
    this.contactForm = document.getElementById('contact-form');

    // Privacy Modal
    this.privacyModal = document.getElementById('privacy-modal');
    this.privacyModalClose = document.getElementById('privacy-modal-close');
    this.privacyModalAck = document.getElementById('privacy-modal-ack');
    this.triggerPrivacyModal = document.getElementById('trigger-privacy-modal');
    this.triggerTermsModal = document.getElementById('trigger-terms-modal');

    // Toast Container
    this.toastHub = document.getElementById('toast-hub');
  }

  /* --------------------------------------------------------------------------
     Pattern 2: Interactive Cursor-Following Spotlight
     -------------------------------------------------------------------------- */
  initSpotlight() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.addEventListener('mousemove', (e) => {
      const cards = document.querySelectorAll('[data-spotlight]');
      cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty('--spotlight-x', `${x}px`);
        card.style.setProperty('--spotlight-y', `${y}px`);
      });
    });
  }

  /* --------------------------------------------------------------------------
     Pattern 3: Global Command Palette (Cmd+K / Ctrl+K)
     -------------------------------------------------------------------------- */
  initCommandPalette() {
    const commands = [
      { id: 'c-verify', title: 'Verify a Product Identifier', cat: 'Navigation', icon: '🔍', action: () => this.jumpTo('#hero-search-section') },
      { id: 'c-scan', title: 'Launch Optical QR Scanner', cat: 'Tools', icon: '📷', action: () => this.openScannerModal() },
      { id: 'c-bento', title: 'Intelligence Bento Dashboard', cat: 'Navigation', icon: '📊', action: () => this.jumpTo('#dashboard-section') },
      { id: 'c-graph', title: 'TruthGraph™ Product Identity Map', cat: 'Navigation', icon: '🗺️', action: () => this.jumpTo('#truthgraph-section') },
      { id: 'c-catalog', title: 'Browse Registered Product Catalog', cat: 'Navigation', icon: '📁', action: () => this.jumpTo('#database-section') },
      { id: 'c-studio', title: 'Product Registration Studio', cat: 'Navigation', icon: '📝', action: () => this.jumpTo('#registration-section') },
      { id: 'c-history', title: 'View Local Investigation History', cat: 'Navigation', icon: '📜', action: () => this.jumpTo('#history-section') },
      { id: 'c-export', title: 'Export Audit History as JSON', cat: 'Tools', icon: '💾', action: () => this.exportHistoryJSON() },
      { id: 'c-sample-aura', title: 'Test: AuraSound Headphones (Match)', cat: 'Sample Investigations', icon: '🟢', action: () => this.runVerification('AUD-9921-X') },
      { id: 'c-sample-nordic', title: 'Test: NordicShield Parka (Warning)', cat: 'Sample Investigations', icon: '🔴', action: () => this.runVerification('NS-8800') },
      { id: 'c-sample-vitalis', title: 'Test: Vitalis Serum (Match)', cat: 'Sample Investigations', icon: '🟢', action: () => this.runVerification('VTL-402') },
      { id: 'c-sample-unlisted', title: 'Test: Unregistered Formula (Inconclusive)', cat: 'Sample Investigations', icon: '🟡', action: () => this.runVerification('UNKNOWN-SAMPLE-99') }
    ];

    this.allCommands = commands;

    // Keyboard shortcut listener
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        this.openCommandPalette();
      }
      if (e.key === 'Escape' && !this.cmdPalette.hidden) {
        this.closeCommandPalette();
      }
    });

    if (this.cmdKTrigger) {
      this.cmdKTrigger.addEventListener('click', () => this.openCommandPalette());
    }

    if (this.cmdCloseBtn) {
      this.cmdCloseBtn.addEventListener('click', () => this.closeCommandPalette());
    }

    this.cmdPalette.addEventListener('click', (e) => {
      if (e.target === this.cmdPalette) this.closeCommandPalette();
    });

    this.cmdSearchInput.addEventListener('input', (e) => {
      this.filterCommands(e.target.value.trim().toLowerCase());
    });
  }

  openCommandPalette() {
    this.cmdPalette.hidden = false;
    this.cmdSearchInput.value = '';
    this.filterCommands('');
    setTimeout(() => this.cmdSearchInput.focus(), 50);
  }

  closeCommandPalette() {
    this.cmdPalette.hidden = true;
  }

  filterCommands(query) {
    const matched = query 
      ? this.allCommands.filter(c => c.title.toLowerCase().includes(query) || c.cat.toLowerCase().includes(query))
      : this.allCommands;

    if (matched.length === 0) {
      this.cmdResultsList.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--ivory-dim); font-size: 0.875rem;">
          No matching commands or actions found for "${this.escapeHtml(query)}"
        </div>
      `;
      return;
    }

    // Group by category
    const groups = {};
    matched.forEach(item => {
      if (!groups[item.cat]) groups[item.cat] = [];
      groups[item.cat].push(item);
    });

    let html = '';
    Object.keys(groups).forEach(cat => {
      html += `<div class="cmd-section-title">${cat}</div>`;
      groups[cat].forEach((cmd, idx) => {
        html += `
          <div class="cmd-item" data-cmd-id="${cmd.id}">
            <div class="cmd-item-left">
              <span>${cmd.icon}</span>
              <span>${this.escapeHtml(cmd.title)}</span>
            </div>
            <span class="cmd-shortcut-tag">↵ Execute</span>
          </div>
        `;
      });
    });

    this.cmdResultsList.innerHTML = html;

    // Attach click events
    this.cmdResultsList.querySelectorAll('.cmd-item').forEach(itemEl => {
      itemEl.addEventListener('click', () => {
        const cmdId = itemEl.getAttribute('data-cmd-id');
        const found = this.allCommands.find(c => c.id === cmdId);
        if (found) {
          this.closeCommandPalette();
          found.action();
        }
      });
    });
  }

  jumpTo(selector) {
    const el = document.querySelector(selector);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }

  /* --------------------------------------------------------------------------
     Event Bindings
     -------------------------------------------------------------------------- */
  bindEvents() {
    // Mobile navigation
    if (this.mobileToggle) {
      this.mobileToggle.addEventListener('click', () => {
        const isOpen = this.mobileToggle.getAttribute('aria-expanded') === 'true';
        this.mobileToggle.setAttribute('aria-expanded', !isOpen);
        this.mobileDrawer.hidden = isOpen;
      });

      document.querySelectorAll('.mobile-nav-link').forEach(link => {
        link.addEventListener('click', () => {
          this.mobileToggle.setAttribute('aria-expanded', 'false');
          this.mobileDrawer.hidden = true;
        });
      });
    }

    // Hero Form Submit
    this.heroForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = this.heroInput.value.trim();
      if (!val) {
        this.heroValidationRow.hidden = false;
        this.heroValidationMsg.textContent = 'Please enter a product SKU, serial number, batch code, or brand name.';
        this.heroInput.focus();
        return;
      }
      this.heroValidationRow.hidden = true;
      this.runVerification(val);
    });

    this.heroInput.addEventListener('input', () => {
      this.heroValidationRow.hidden = true;
      if (this.heroLogStream) {
        this.heroLogStream.textContent = this.heroInput.value.trim() 
          ? `Input stream: "${this.heroInput.value.trim()}" · Ready for execution`
          : 'Listening for input identifier on TruthTag global node...';
      }
    });

    // Hero Quick Demo Chips
    this.heroQuickChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const q = chip.getAttribute('data-query');
        this.heroInput.value = q;
        this.runVerification(q);
      });
    });

    // Scanner Triggers
    if (this.headerScannerBtn) this.headerScannerBtn.addEventListener('click', () => this.openScannerModal());
    if (this.mobileScannerTrigger) this.mobileScannerTrigger.addEventListener('click', () => {
      this.mobileDrawer.hidden = true;
      this.openScannerModal();
    });
    if (this.tileOpenScanner) this.tileOpenScanner.addEventListener('click', () => this.openScannerModal());

    // Scanner Modal
    if (this.scannerModalClose) this.scannerModalClose.addEventListener('click', () => this.closeScannerModal());
    this.scannerPresetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const val = btn.getAttribute('data-scan-val');
        this.closeScannerModal();
        this.showToast(`Optical Tag Decoded: "${val}"`, 'info');
        this.heroInput.value = val;
        this.runVerification(val);
      });
    });

    if (this.modalCameraToggleBtn) {
      this.modalCameraToggleBtn.addEventListener('click', () => this.toggleModalWebcam());
    }

    if (this.modalQrFile) {
      this.modalQrFile.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          const fname = e.target.files[0].name.toLowerCase();
          this.closeScannerModal();
          this.showToast(`Analyzing packaging scan: ${fname}...`, 'info');
          let payload = 'AUD-9921-X';
          if (fname.includes('warn') || fname.includes('nordic') || fname.includes('fake')) payload = 'NS-8800';
          else if (fname.includes('serum') || fname.includes('vitalis')) payload = 'VTL-402';
          setTimeout(() => {
            this.heroInput.value = payload;
            this.runVerification(payload);
          }, 800);
        }
      });
    }

    // Dossier Tabs Navigation
    this.dossierTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetId = tab.getAttribute('data-tab');
        this.dossierTabs.forEach(t => t.classList.remove('active'));
        this.dossierPanels.forEach(p => {
          p.classList.remove('active');
          p.hidden = true;
        });

        tab.classList.add('active');
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) {
          targetPanel.classList.add('active');
          targetPanel.hidden = false;
        }
      });
    });

    // Dossier Action Buttons
    if (this.btnPrintDossier) this.btnPrintDossier.addEventListener('click', () => window.print());
    if (this.btnCopyDossierLink) {
      this.btnCopyDossierLink.addEventListener('click', () => {
        if (this.currentInvestigation) {
          navigator.clipboard?.writeText(this.currentInvestigation.recordDigest).then(() => {
            this.showToast('Cryptographic audit digest copied to clipboard!', 'success');
          }).catch(() => {
            this.showToast(`Audit ID: ${this.currentInvestigation.auditId}`, 'info');
          });
        }
      });
    }
    if (this.btnNewInvestigation) {
      this.btnNewInvestigation.addEventListener('click', (e) => {
        e.preventDefault();
        this.heroInput.value = '';
        this.jumpTo('#hero-search-section');
        this.heroInput.focus();
      });
    }

    // Bento Action Buttons
    if (this.tileRegisterProduct) this.tileRegisterProduct.addEventListener('click', () => this.jumpTo('#registration-section'));
    if (this.tileExportAudit) this.tileExportAudit.addEventListener('click', () => this.exportHistoryJSON());
    if (this.tileOpenCmd) this.tileOpenCmd.addEventListener('click', () => this.openCommandPalette());

    // Catalog Search & Filters
    this.catalogPills.forEach(pill => {
      pill.addEventListener('click', () => {
        this.catalogPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.catalogFilter = pill.getAttribute('data-category');
        this.renderCatalog();
      });
    });

    if (this.catalogSearchInput) {
      this.catalogSearchInput.addEventListener('input', (e) => {
        this.catalogSearch = e.target.value.toLowerCase().trim();
        this.renderCatalog();
      });
    }

    // Protocol Timeline Interactive Cards
    this.timelineCards.forEach(card => {
      card.addEventListener('click', () => {
        this.timelineCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        const step = card.getAttribute('data-step');
        this.showToast(`Previewing Investigation Phase 0${step}`, 'info');
      });
    });

    // Registration Studio (Multi-Step Wizard)
    if (this.wizNext1) this.wizNext1.addEventListener('click', () => this.advanceWizard(1));
    if (this.wizPrev2) this.wizPrev2.addEventListener('click', () => this.stepWizardBack(2));
    if (this.wizNext2) this.wizNext2.addEventListener('click', () => this.advanceWizard(2));
    if (this.wizPrev3) this.wizPrev3.addEventListener('click', () => this.stepWizardBack(3));
    if (this.wizNext3) this.wizNext3.addEventListener('click', () => this.advanceWizard(3));
    if (this.wizPrev4) this.wizPrev4.addEventListener('click', () => this.stepWizardBack(4));

    if (this.studioForm) {
      this.studioForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.finalizeRegistration();
      });
    }

    // History Filters & Actions
    this.historyFilterPills.forEach(pill => {
      pill.addEventListener('click', () => {
        this.historyFilterPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.historyFilter = pill.getAttribute('data-hstatus');
        this.renderHistory();
      });
    });

    if (this.historySearchField) {
      this.historySearchField.addEventListener('input', (e) => {
        this.historySearch = e.target.value.toLowerCase().trim();
        this.renderHistory();
      });
    }

    if (this.histExportBtn) this.histExportBtn.addEventListener('click', () => this.exportHistoryJSON());
    if (this.histClearBtn) {
      this.histClearBtn.addEventListener('click', () => {
        if (confirm('Clear all local investigation audit logs?')) {
          TruthTagDB.clearHistory();
          this.renderHistory();
          this.renderBentoDashboard();
          this.showToast('Audit history cleared.', 'info');
        }
      });
    }

    // FAQs Accordion
    this.faqItems.forEach(item => {
      const trigger = item.querySelector('.faq-trigger');
      const drawer = item.querySelector('.faq-drawer');
      trigger.addEventListener('click', () => {
        const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
        this.faqItems.forEach(other => {
          if (other !== item) {
            other.classList.remove('active');
            other.querySelector('.faq-trigger').setAttribute('aria-expanded', 'false');
            other.querySelector('.faq-drawer').hidden = true;
          }
        });
        trigger.setAttribute('aria-expanded', !isExpanded);
        item.classList.toggle('active', !isExpanded);
        drawer.hidden = isExpanded;
      });
    });

    // Contact Form
    if (this.contactForm) {
      this.contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleContactSubmit();
      });
    }

    // Privacy Modal
    if (this.triggerPrivacyModal) this.triggerPrivacyModal.addEventListener('click', () => this.privacyModal.hidden = false);
    if (this.triggerTermsModal) this.triggerTermsModal.addEventListener('click', () => this.privacyModal.hidden = false);
    if (this.privacyModalClose) this.privacyModalClose.addEventListener('click', () => this.privacyModal.hidden = true);
    if (this.privacyModalAck) this.privacyModalAck.addEventListener('click', () => this.privacyModal.hidden = true);
  }

  /* --------------------------------------------------------------------------
     Core Investigation Execution Pipeline
     -------------------------------------------------------------------------- */
  runVerification(query) {
    if (!query) return;

    // Scroll to workspace
    this.jumpTo('#investigation-workspace');
    this.dossierWrapper.hidden = true;
    this.loader.hidden = false;

    // Multi-phase telemetry loading animation
    this.loaderFill.style.width = '20%';
    this.loaderMainMsg.textContent = 'Ingesting packaging identifier...';
    this.loaderSubMsg.textContent = `Target: "${query}" · Normalizing character matrix`;
    this.termPill1.className = 'pill-mini active';
    this.termPill2.className = 'pill-mini';
    this.termPill3.className = 'pill-mini';

    setTimeout(() => {
      this.loaderFill.style.width = '65%';
      this.loaderMainMsg.textContent = 'Querying brand authority ledger & checking batch collision indices...';
      this.loaderSubMsg.textContent = 'Cross-referencing cryptographic factory allocation parameters';
      this.termPill2.className = 'pill-mini active';
    }, 400);

    setTimeout(() => {
      this.loaderFill.style.width = '95%';
      this.loaderMainMsg.textContent = 'Synthesizing evidence-based investigation dossier...';
      this.loaderSubMsg.textContent = 'Validating physical security features and threat signal logs';
      this.termPill3.className = 'pill-mini active';
    }, 750);

    setTimeout(() => {
      this.loader.hidden = true;
      const result = TruthTagVerifier.verify(query);
      if (!result) return;

      this.currentInvestigation = result;

      // Save to localStorage history
      TruthTagDB.addHistory(result);

      // Render Dossier
      this.renderDossier(result);

      // Update Bento Dashboard metrics & stream
      this.renderBentoDashboard();

      // Update History view
      this.renderHistory();

      // Toast feedback
      if (result.status === 'match') {
        this.showToast('Record Match Confirmed in Brand Registry', 'success');
      } else if (result.status === 'warning') {
        this.showToast('WARNING: Threat Anomaly / Counterfeit Risk Detected', 'error');
      } else {
        this.showToast('Notice: Verification Inconclusive (Unregistered Identifier)', 'info');
      }
    }, 1050);
  }

  /* --------------------------------------------------------------------------
     Investigation Dossier Renderer
     -------------------------------------------------------------------------- */
  renderDossier(dossier) {
    const isMatch = dossier.status === 'match';
    const isWarning = dossier.status === 'warning';

    // Header Class
    this.dossierHeader.className = `dossier-header ${dossier.status}`;

    this.dossierHeader.innerHTML = `
      <div>
        <span class="dossier-status-pill">
          ${isMatch ? '● RECORD MATCH FOUND' : (isWarning ? '▲ POTENTIAL INCONSISTENCY / WARNING' : '■ INCONCLUSIVE')}
        </span>
        <h2 class="dossier-title">${this.escapeHtml(dossier.productName)}</h2>
        <div class="dossier-meta">
          <span>Authority: <strong>${this.escapeHtml(dossier.brand)}</strong></span>
          <span>•</span>
          <span>Category: ${this.escapeHtml(dossier.category)}</span>
          <span>•</span>
          <span>Audit Ref: <code>${dossier.auditId}</code></span>
        </div>
      </div>
      <div class="dossier-hash-block">
        <span class="mono-meta">Cryptographic Digest</span>
        <span class="mono-hash">${dossier.recordDigest.slice(0, 24)}...</span>
        <span class="mono-meta" style="margin-top: 4px;">Timestamp: ${dossier.timestamp}</span>
      </div>
    `;

    // 1. Consistency Inspector Table
    this.inspectorTableBody.innerHTML = dossier.consistencyMatrix.map(row => {
      let badgeClass = 'match';
      let badgeLabel = 'EXACT MATCH';
      if (row.status === 'conflict') {
        badgeClass = 'conflict';
        badgeLabel = 'CONFLICT / ALERT';
      } else if (row.status === 'missing') {
        badgeClass = 'missing';
        badgeLabel = 'UNREGISTERED';
      }

      return `
        <tr>
          <td><strong>${this.escapeHtml(row.field)}</strong></td>
          <td><code class="font-mono">${this.escapeHtml(row.submitted)}</code></td>
          <td><code class="font-mono">${this.escapeHtml(row.registered)}</code></td>
          <td><span class="status-cell-badge ${badgeClass}">${badgeLabel}</span></td>
          <td style="font-size: 0.8125rem; color: var(--ivory-muted);">${this.escapeHtml(row.note)}</td>
        </tr>
      `;
    }).join('');

    const matchedScore = dossier.consistencyMatrix.filter(r => r.status === 'match').length;
    this.inspectorScoreBadge.textContent = `${matchedScore}/5 PARAMETERS VALIDATED`;
    if (matchedScore === 5) {
      this.inspectorScoreBadge.style.color = 'var(--accent-lime)';
    } else if (isWarning) {
      this.inspectorScoreBadge.style.color = 'var(--status-warning)';
      this.inspectorScoreBadge.textContent = `ANOMALY DETECTED IN RECORD`;
    } else {
      this.inspectorScoreBadge.style.color = 'var(--status-inconclusive)';
    }

    // 2. TruthGraph Relational Map
    this.renderTruthGraphSVG(dossier);

    // 3. Provenance & Previous Checks
    document.getElementById('prov-authority').textContent = dossier.brand;
    document.getElementById('prov-timestamp').textContent = dossier.productionDate;
    document.getElementById('prov-digest').textContent = dossier.recordDigest;
    document.getElementById('prov-channels').textContent = dossier.authorizedChannels;

    const trail = TruthTagDB.getHistory().filter(h => h.productId === dossier.productId);
    const trailEl = document.getElementById('prov-audit-trail');
    if (trail.length > 0) {
      trailEl.innerHTML = trail.slice(0, 5).map(t => `
        <li class="trail-item">
          <span>Query: <code class="font-mono">${this.escapeHtml(t.submittedQuery)}</code></span>
          <span class="mono-meta">${t.timestamp}</span>
        </li>
      `).join('');
    } else {
      trailEl.innerHTML = '<li class="trail-item"><span class="mono-meta">No prior checks recorded in local audit trail.</span></li>';
    }

    // 4. Physical Authentication Guide
    this.physicalGuideContainer.innerHTML = `
      <div class="guide-step-card">
        <div class="guide-step-num">1</div>
        <div class="guide-step-info">
          <h4>Inspect Registered Packaging Security Seal</h4>
          <p>This product line is registered with: <strong>${this.escapeHtml(dossier.securityFeature)}</strong>. Verify that the outer carton bears an intact seal matching this exact specification.</p>
        </div>
      </div>
      <div class="guide-step-card">
        <div class="guide-step-num">2</div>
        <div class="guide-step-info">
          <h4>Production Facility &amp; Origin Cross-Check</h4>
          <p>Authorized factory on record: <strong>${this.escapeHtml(dossier.facility)}</strong>. Ensure packaging markings and country of origin labels correspond.</p>
        </div>
      </div>
      <div class="guide-step-card">
        <div class="guide-step-num">3</div>
        <div class="guide-step-info">
          <h4>Authorized Distributor Verification</h4>
          <p>Genuine units are distributed via: <strong>${this.escapeHtml(dossier.authorizedChannels)}</strong>. Be wary of unauthorized marketplace storefronts offering abnormal 60%+ discounts.</p>
        </div>
      </div>
    `;

    // Make dossier visible & default to tab 1
    this.dossierWrapper.hidden = false;
    document.querySelector('.dossier-tab[data-tab="tab-evidence"]').click();
  }

  /* --------------------------------------------------------------------------
     TruthGraph™ Relational SVG Renderer
     -------------------------------------------------------------------------- */
  renderTruthGraphSVG(dossier) {
    const isMatch = dossier.status === 'match';
    const isWarning = dossier.status === 'warning';
    const statusColor = isMatch ? '#A3E635' : (isWarning ? '#EF4444' : '#F59E0B');

    const nodes = [
      { id: 'brand', label: dossier.brand, sub: 'Brand Authority', x: 120, y: 190, color: '#A3E635', r: 36, details: `Accredited Brand Authority: ${dossier.brand}. Registered cryptographic issuer.` },
      { id: 'facility', label: 'Factory Plant', sub: dossier.facility.split(',')[0], x: 280, y: 80, color: '#10B981', r: 30, details: `Manufacturing Facility: ${dossier.facility}. Validated production facility.` },
      { id: 'product', label: dossier.productId, sub: 'Model SKU', x: 420, y: 190, color: statusColor, r: 38, details: `Product Model: ${dossier.productName} (SKU: ${dossier.productId}).` },
      { id: 'batch', label: dossier.batch, sub: 'Batch / Lot', x: 580, y: 100, color: isWarning ? '#EF4444' : '#A3E635', r: 32, details: `Batch Code: ${dossier.batch}. Production allocation verification.` },
      { id: 'serial', label: dossier.serial, sub: 'Serial Identifier', x: 700, y: 220, color: statusColor, r: 34, details: `Unit Serial: ${dossier.serial}. Individual cryptographic serialization.` },
      { id: 'seal', label: 'Security Seal', sub: dossier.securityFeature.split('&')[0], x: 480, y: 320, color: '#38BDF8', r: 28, details: `Physical Seal Profile: ${dossier.securityFeature}.` }
    ];

    const links = [
      { from: nodes[0], to: nodes[1] },
      { from: nodes[0], to: nodes[2] },
      { from: nodes[1], to: nodes[3] },
      { from: nodes[2], to: nodes[3] },
      { from: nodes[3], to: nodes[4] },
      { from: nodes[2], to: nodes[5] }
    ];

    let svgHtml = `
      <defs>
        <filter id="node-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
    `;

    // Render connection lines
    links.forEach(link => {
      svgHtml += `
        <line x1="${link.from.x}" y1="${link.from.y}" x2="${link.to.x}" y2="${link.to.y}" class="tg-link"/>
      `;
    });

    // Render nodes
    nodes.forEach(node => {
      svgHtml += `
        <g class="tg-node" data-node-id="${node.id}" data-details="${this.escapeHtml(node.details)}" transform="translate(${node.x}, ${node.y})">
          <circle cx="0" cy="0" r="${node.r}" fill="#0A140F" stroke="${node.color}" stroke-width="2" filter="url(#node-glow)"/>
          <text text-anchor="middle" y="-4" fill="#FFFFFF" font-family="Plus Jakarta Sans" font-size="11" font-weight="700">${this.escapeHtml(node.label.length > 15 ? node.label.slice(0, 13) + '..' : node.label)}</text>
          <text text-anchor="middle" y="12" fill="${node.color}" font-family="JetBrains Mono" font-size="8">${this.escapeHtml(node.sub.length > 18 ? node.sub.slice(0, 16) + '..' : node.sub)}</text>
        </g>
      `;
    });

    this.truthgraphSvg.innerHTML = svgHtml;

    // Attach click listener on nodes
    this.truthgraphSvg.querySelectorAll('.tg-node').forEach(nodeEl => {
      nodeEl.addEventListener('click', () => {
        const details = nodeEl.getAttribute('data-details');
        this.nodeInspectorText.textContent = details;
        this.showToast('TruthGraph Entity Focused', 'info');
      });
    });
  }

  /* --------------------------------------------------------------------------
     TruthGraph Global Preview Section
     -------------------------------------------------------------------------- */
  initTruthGraphPreview() {
    const previewEl = document.getElementById('global-truthgraph-demo');
    if (!previewEl) return;

    previewEl.innerHTML = `
      <svg viewBox="0 0 440 220" style="width: 100%; height: 100%;">
        <line x1="60" y1="110" x2="160" y2="50" stroke="rgba(163,230,53,0.3)" stroke-width="1.5" stroke-dasharray="3"/>
        <line x1="60" y1="110" x2="160" y2="160" stroke="rgba(163,230,53,0.3)" stroke-width="1.5" stroke-dasharray="3"/>
        <line x1="160" y1="50" x2="280" y2="110" stroke="rgba(163,230,53,0.3)" stroke-width="1.5" stroke-dasharray="3"/>
        <line x1="160" y1="160" x2="280" y2="110" stroke="rgba(163,230,53,0.3)" stroke-width="1.5" stroke-dasharray="3"/>
        <line x1="280" y1="110" x2="380" y2="110" stroke="#A3E635" stroke-width="2"/>

        <g transform="translate(60, 110)">
          <circle cx="0" cy="0" r="24" fill="#0A140F" stroke="#A3E635" stroke-width="2"/>
          <text text-anchor="middle" y="4" fill="#A3E635" font-family="JetBrains Mono" font-size="9" font-weight="700">BRAND</text>
        </g>
        <g transform="translate(160, 50)">
          <circle cx="0" cy="0" r="20" fill="#0A140F" stroke="#10B981" stroke-width="1.5"/>
          <text text-anchor="middle" y="3" fill="#FFF" font-family="JetBrains Mono" font-size="8">FACILITY</text>
        </g>
        <g transform="translate(160, 160)">
          <circle cx="0" cy="0" r="20" fill="#0A140F" stroke="#10B981" stroke-width="1.5"/>
          <text text-anchor="middle" y="3" fill="#FFF" font-family="JetBrains Mono" font-size="8">SEAL</text>
        </g>
        <g transform="translate(280, 110)">
          <circle cx="0" cy="0" r="24" fill="#0A140F" stroke="#A3E635" stroke-width="2"/>
          <text text-anchor="middle" y="4" fill="#A3E635" font-family="JetBrains Mono" font-size="9" font-weight="700">BATCH</text>
        </g>
        <g transform="translate(380, 110)">
          <circle cx="0" cy="0" r="22" fill="#0A140F" stroke="#A3E635" stroke-width="2"/>
          <text text-anchor="middle" y="4" fill="#BEF264" font-family="JetBrains Mono" font-size="9" font-weight="700">UNIT SN</text>
        </g>
      </svg>
    `;
  }

  /* --------------------------------------------------------------------------
     Pattern 4: Bento-Grid Intelligence Dashboard Engine
     -------------------------------------------------------------------------- */
  renderBentoDashboard() {
    const history = TruthTagDB.getHistory();
    const allRecords = TruthTagDB.getAllRecords();

    const total = history.length;
    const matches = history.filter(h => h.status === 'match').length;
    const warnings = history.filter(h => h.status === 'warning').length;
    const inconclusive = history.filter(h => h.status === 'inconclusive').length;

    // Numerical counters
    this.bentoTotalChecks.textContent = total;
    this.bentoMatchedCount.textContent = matches;
    this.bentoWarningCount.textContent = warnings;
    this.bentoInconclusiveCount.textContent = inconclusive;
    this.bentoLedgerCapacity.textContent = allRecords.length;

    // Donut SVG calculations (circumference = 2 * PI * 38 ≈ 238.76)
    const circ = 238.76;
    if (total === 0) {
      this.donutSegMatch.style.strokeDashoffset = '0';
      this.donutSegWarning.style.strokeDashoffset = `${circ}`;
      this.donutSegInconclusive.style.strokeDashoffset = `${circ}`;
      this.donutCenterRate.textContent = '100%';
    } else {
      const matchPct = matches / total;
      const warnPct = warnings / total;
      const inconcPct = inconclusive / total;

      const matchOffset = circ - (circ * matchPct);
      this.donutSegMatch.style.strokeDashoffset = `${matchOffset}`;
      this.donutCenterRate.textContent = `${Math.round(matchPct * 100)}%`;
    }

    // Recent telemetry stream
    if (history.length === 0) {
      this.bentoStreamList.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--ivory-dim); font-size: 0.8125rem;">
          No live query activity recorded yet. Run a product verification above.
        </div>
      `;
    } else {
      this.bentoStreamList.innerHTML = history.slice(0, 5).map(item => `
        <div class="stream-row">
          <div class="stream-left">
            <span class="stream-badge ${item.status}">${item.status === 'match' ? 'MATCH' : (item.status === 'warning' ? 'ALERT' : 'UNLISTED')}</span>
            <span class="stream-sku">${this.escapeHtml(item.productId)}</span>
            <span class="stream-product">• ${this.escapeHtml(item.productName.slice(0, 22))}...</span>
          </div>
          <span class="stream-time">${item.timestamp}</span>
        </div>
      `).join('');
    }

    // Category distribution bars
    const categories = ['Electronics', 'Skincare', 'Footwear', 'Apparel', 'Luxury'];
    this.bentoCategoryBars.innerHTML = categories.map(cat => {
      const count = allRecords.filter(r => r.category.toLowerCase() === cat.toLowerCase()).length;
      const pct = Math.min(100, Math.round((count / allRecords.length) * 100));
      return `
        <div class="cat-bar-item">
          <div class="cat-bar-meta">
            <span>${cat}</span>
            <span class="mono">${count} records (${pct}%)</span>
          </div>
          <div class="cat-progress-track">
            <div class="cat-progress-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  /* --------------------------------------------------------------------------
     Catalog & Registered Product Explorer
     -------------------------------------------------------------------------- */
  renderCatalog() {
    const allRecords = TruthTagDB.getAllRecords();
    const customRecords = TruthTagDB.getCustomRecords();
    const customIds = new Set(customRecords.map(r => r.id));

    let filtered = allRecords;

    if (this.catalogFilter === 'custom') {
      filtered = allRecords.filter(r => customIds.has(r.id));
    } else if (this.catalogFilter !== 'all') {
      filtered = allRecords.filter(r => r.category.toLowerCase() === this.catalogFilter.toLowerCase());
    }

    if (this.catalogSearch) {
      filtered = filtered.filter(r => 
        r.name.toLowerCase().includes(this.catalogSearch) ||
        r.brand.toLowerCase().includes(this.catalogSearch) ||
        r.productId.toLowerCase().includes(this.catalogSearch) ||
        r.batch.toLowerCase().includes(this.catalogSearch) ||
        r.serial.toLowerCase().includes(this.catalogSearch)
      );
    }

    if (filtered.length === 0) {
      this.catalogGrid.innerHTML = '';
      this.catalogEmptyState.hidden = false;
      return;
    }

    this.catalogEmptyState.hidden = true;

    this.catalogGrid.innerHTML = filtered.map(item => {
      const isCustom = customIds.has(item.id);
      const isWarning = item.status === 'warning';

      return `
        <div class="catalog-item-card spotlight-card" data-spotlight>
          <div class="cat-card-top">
            <span class="cat-card-sku font-mono">${this.escapeHtml(item.productId)}</span>
            <span class="cat-card-status ${isWarning ? 'warning' : 'match'}">
              ${isWarning ? '▲ ALERT LOT' : '● REGISTERED'}
            </span>
          </div>

          <h3 class="cat-card-name">${this.escapeHtml(item.name)}</h3>
          <div class="cat-card-brand">${this.escapeHtml(item.brand)} • ${this.escapeHtml(item.category)} ${isCustom ? '<span style="color:var(--accent-lime);">(Custom)</span>' : ''}</div>

          <div class="cat-card-details font-mono">
            <div class="card-detail-row">
              <span style="color: var(--ivory-dim);">Batch Lot:</span>
              <span>${this.escapeHtml(item.batch)}</span>
            </div>
            <div class="card-detail-row">
              <span style="color: var(--ivory-dim);">Serial Ref:</span>
              <span>${this.escapeHtml(item.serial)}</span>
            </div>
            <div class="card-detail-row">
              <span style="color: var(--ivory-dim);">Facility:</span>
              <span>${this.escapeHtml(item.facility.split(',')[0])}</span>
            </div>
          </div>

          <div class="cat-card-actions">
            <button type="button" class="btn btn-outline-lime btn-sm btn-block catalog-verify-btn" data-sku="${this.escapeHtml(item.productId)}">
              Run Investigation →
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Attach click listeners to catalog verify buttons
    this.catalogGrid.querySelectorAll('.catalog-verify-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const sku = btn.getAttribute('data-sku');
        this.heroInput.value = sku;
        this.runVerification(sku);
      });
    });
  }

  /* --------------------------------------------------------------------------
     Product Registration Studio (Multi-Step Wizard)
     -------------------------------------------------------------------------- */
  advanceWizard(step) {
    // Validate current step
    if (step === 1) {
      const name = document.getElementById('reg-name').value.trim();
      const brand = document.getElementById('reg-brand').value.trim();
      const cat = document.getElementById('reg-category').value;

      document.getElementById('err-reg-name').textContent = '';
      document.getElementById('err-reg-brand').textContent = '';
      document.getElementById('err-reg-category').textContent = '';

      let err = false;
      if (!name) { document.getElementById('err-reg-name').textContent = 'Product name required.'; err = true; }
      if (!brand) { document.getElementById('err-reg-brand').textContent = 'Brand authority required.'; err = true; }
      if (!cat) { document.getElementById('err-reg-category').textContent = 'Select a sector.'; err = true; }
      if (err) return;

      this.wizardData.name = name;
      this.wizardData.brand = brand;
      this.wizardData.category = cat;
      this.switchWizardStep(2);
    } else if (step === 2) {
      const sku = document.getElementById('reg-sku').value.trim();
      const batch = document.getElementById('reg-batch').value.trim();
      const serial = document.getElementById('reg-serial').value.trim();

      document.getElementById('err-reg-sku').textContent = '';
      document.getElementById('err-reg-batch').textContent = '';
      document.getElementById('err-reg-serial').textContent = '';

      let err = false;
      if (!sku) { document.getElementById('err-reg-sku').textContent = 'Product SKU required.'; err = true; }
      if (!batch) { document.getElementById('err-reg-batch').textContent = 'Batch code required.'; err = true; }
      if (!serial) { document.getElementById('err-reg-serial').textContent = 'Serial number required.'; err = true; }
      if (err) return;

      this.wizardData.productId = sku;
      this.wizardData.batch = batch;
      this.wizardData.serial = serial;
      this.switchWizardStep(3);
    } else if (step === 3) {
      const facility = document.getElementById('reg-facility').value.trim();
      const secType = document.getElementById('reg-security-type').value;
      const channels = document.getElementById('reg-channels').value.trim();
      const notes = document.getElementById('reg-packaging-notes').value.trim();

      document.getElementById('err-reg-facility').textContent = '';
      if (!facility) {
        document.getElementById('err-reg-facility').textContent = 'Manufacturing facility location required.';
        return;
      }

      this.wizardData.facility = facility;
      this.wizardData.securityFeature = secType;
      this.wizardData.authorizedChannels = channels || 'Authorized Brand Network';
      this.wizardData.notes = notes || 'Standard packaging security inspection guidelines apply.';

      // Populate Step 4 review
      this.studioReviewSummary.innerHTML = `
        <div><strong>Product:</strong> ${this.escapeHtml(this.wizardData.name)}</div>
        <div><strong>Brand:</strong> ${this.escapeHtml(this.wizardData.brand)}</div>
        <div><strong>Category:</strong> ${this.escapeHtml(this.wizardData.category)}</div>
        <div><strong>SKU:</strong> <code class="font-mono">${this.escapeHtml(this.wizardData.productId)}</code></div>
        <div><strong>Batch Lot:</strong> <code class="font-mono">${this.escapeHtml(this.wizardData.batch)}</code></div>
        <div><strong>Serial:</strong> <code class="font-mono">${this.escapeHtml(this.wizardData.serial)}</code></div>
        <div><strong>Facility:</strong> ${this.escapeHtml(this.wizardData.facility)}</div>
        <div><strong>Security Feature:</strong> ${this.escapeHtml(this.wizardData.securityFeature)}</div>
      `;

      this.switchWizardStep(4);
    }
  }

  stepWizardBack(current) {
    this.switchWizardStep(current - 1);
  }

  switchWizardStep(stepNum) {
    this.activeWizardStep = stepNum;
    this.wizPanes.forEach((pane, idx) => {
      pane.classList.toggle('active', (idx + 1) === stepNum);
      pane.hidden = (idx + 1) !== stepNum;
    });
    this.wizPills.forEach((pill, idx) => {
      pill.classList.toggle('active', (idx + 1) === stepNum);
    });
  }

  finalizeRegistration() {
    const recordDigest = 'SHA256: ' + Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2);
    const newRecord = {
      id: 'custom-' + Date.now(),
      name: this.wizardData.name,
      brand: this.wizardData.brand,
      category: this.wizardData.category,
      productId: this.wizardData.productId,
      batch: this.wizardData.batch,
      serial: this.wizardData.serial,
      status: 'match',
      facility: this.wizardData.facility,
      productionDate: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      authorizedChannels: this.wizardData.authorizedChannels,
      securityFeature: this.wizardData.securityFeature,
      notes: this.wizardData.notes,
      recordDigest: recordDigest,
      reason: `Authorized Brand Enrollment: Registered via TruthTag Studio. Cryptographically validated for authentic manufacturing run.`
    };

    TruthTagDB.saveCustomRecord(newRecord);
    this.studioForm.reset();
    this.switchWizardStep(1);
    this.renderCatalog();
    this.renderBentoDashboard();

    this.showToast(`Product "${newRecord.name}" successfully enrolled in ledger!`, 'success');

    // Prompt user to verify the newly registered product
    setTimeout(() => {
      if (confirm(`Product enrolled! Would you like to run an instant investigation on SKU "${newRecord.productId}"?`)) {
        this.heroInput.value = newRecord.productId;
        this.runVerification(newRecord.productId);
      }
    }, 400);
  }

  /* --------------------------------------------------------------------------
     Investigation Audit History Renderer
     -------------------------------------------------------------------------- */
  renderHistory() {
    const history = TruthTagDB.getHistory();

    // Counts for filter pills
    const matchCount = history.filter(h => h.status === 'match').length;
    const warnCount = history.filter(h => h.status === 'warning').length;
    const inconcCount = history.filter(h => h.status === 'inconclusive').length;

    this.hCountAll.textContent = history.length;
    this.hCountMatch.textContent = matchCount;
    this.hCountWarning.textContent = warnCount;
    this.hCountInconclusive.textContent = inconcCount;

    let filtered = history;
    if (this.historyFilter !== 'all') {
      filtered = filtered.filter(h => h.status === this.historyFilter);
    }

    if (this.historySearch) {
      filtered = filtered.filter(h => 
        (h.productName && h.productName.toLowerCase().includes(this.historySearch)) ||
        (h.productId && h.productId.toLowerCase().includes(this.historySearch)) ||
        (h.submittedQuery && h.submittedQuery.toLowerCase().includes(this.historySearch)) ||
        (h.brand && h.brand.toLowerCase().includes(this.historySearch))
      );
    }

    if (filtered.length === 0) {
      this.historyList.innerHTML = '';
      this.historyList.hidden = true;
      this.historyEmptyView.hidden = false;
      return;
    }

    this.historyEmptyView.hidden = true;
    this.historyList.hidden = false;

    this.historyList.innerHTML = filtered.map(item => `
      <div class="history-log-row" data-history-id="${item.id}">
        <div class="log-left">
          <div class="log-status-dot ${item.status}"></div>
          <div>
            <div class="log-title">${this.escapeHtml(item.productName)}</div>
            <div class="log-sub">
              <span>Authority: <strong>${this.escapeHtml(item.brand)}</strong></span>
              <span>•</span>
              <span>Query: <code class="font-mono">${this.escapeHtml(item.submittedQuery)}</code></span>
              <span>•</span>
              <span>${item.timestamp}</span>
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button type="button" class="btn btn-outline btn-sm view-dossier-btn">Inspect Dossier</button>
          <button type="button" class="btn btn-outline btn-sm danger-text delete-log-btn" title="Delete log">&times;</button>
        </div>
      </div>
    `).join('');

    // Attach row listeners
    this.historyList.querySelectorAll('.view-dossier-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const row = e.target.closest('.history-log-row');
        const id = row.getAttribute('data-history-id');
        const record = history.find(h => h.id === id);
        if (record) {
          this.currentInvestigation = record;
          this.renderDossier(record);
          this.jumpTo('#investigation-workspace');
          this.showToast(`Restored dossier for ${record.productName}`, 'info');
        }
      });
    });

    this.historyList.querySelectorAll('.delete-log-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const row = e.target.closest('.history-log-row');
        const id = row.getAttribute('data-history-id');
        TruthTagDB.deleteHistoryItem(id);
        this.renderHistory();
        this.renderBentoDashboard();
        this.showToast('Log entry removed.', 'info');
      });
    });
  }

  exportHistoryJSON() {
    const history = TruthTagDB.getHistory();
    if (history.length === 0) {
      this.showToast('No history records to export.', 'info');
      return;
    }
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2));
    const dl = document.createElement('a');
    dl.setAttribute('href', dataStr);
    dl.setAttribute('download', `truthtag_audit_dossier_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(dl);
    dl.click();
    dl.remove();
    this.showToast('Exported audit history JSON file.', 'success');
  }

  /* --------------------------------------------------------------------------
     Optical Camera / QR Scanner Viewport
     -------------------------------------------------------------------------- */
  openScannerModal() {
    this.scannerModal.hidden = false;
  }

  closeScannerModal() {
    this.stopModalWebcam();
    this.scannerModal.hidden = true;
  }

  async toggleModalWebcam() {
    if (this.webcamStream) {
      this.stopModalWebcam();
      this.modalCameraToggleBtn.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        <span>Use Real Camera</span>
      `;
      return;
    }

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.showToast('Camera API not accessible in this environment. Please use simulated optical presets.', 'info');
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      this.webcamStream = stream;
      this.modalWebcamVideo.srcObject = stream;
      this.modalWebcamVideo.style.display = 'block';
      this.modalWebcamVideo.play();
      this.modalScannerIdle.style.display = 'none';

      this.modalCameraToggleBtn.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="1" y1="1" x2="23" y2="23"/>
          <path d="M21 21H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3m3-3h6l2 3h4a2 2 0 0 1 2 2v9.34m-7.72-2.06a4 4 0 1 1-5.56-5.56"/>
        </svg>
        <span>Turn Off Camera</span>
      `;
      this.showToast('Hardware optical camera active. Align packaging tag in reticle.', 'info');
    } catch (err) {
      console.warn('Camera error', err);
      this.showToast('Camera access unavailable. Using optical presets.', 'info');
    }
  }

  stopModalWebcam() {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach(t => t.stop());
      this.webcamStream = null;
    }
    this.modalWebcamVideo.style.display = 'none';
    this.modalScannerIdle.style.display = 'block';
  }

  /* --------------------------------------------------------------------------
     Contact & Incident Reporting Handler
     -------------------------------------------------------------------------- */
  handleContactSubmit() {
    const name = document.getElementById('c-name').value.trim();
    const email = document.getElementById('c-email').value.trim();
    const msg = document.getElementById('c-message').value.trim();

    let err = false;
    document.querySelectorAll('#contact-form .field-error').forEach(e => e.textContent = '');

    if (!name) { document.getElementById('err-c-name').textContent = 'Reporter name required.'; err = true; }
    if (!email || !email.includes('@')) { document.getElementById('err-c-email').textContent = 'Valid email required.'; err = true; }
    if (!msg) { document.getElementById('err-c-message').textContent = 'Incident message required.'; err = true; }
    if (err) return;

    this.contactForm.reset();
    this.showToast('Incident report logged. Intelligence desk notified.', 'success');
  }

  /* --------------------------------------------------------------------------
     Global Toast Hub
     -------------------------------------------------------------------------- */
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-pill toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✓';
    if (type === 'error') icon = '⚠';

    toast.innerHTML = `
      <span style="font-weight: 800; color: ${type === 'success' ? 'var(--accent-lime)' : (type === 'error' ? 'var(--status-warning)' : '#38BDF8')}">${icon}</span>
      <span>${this.escapeHtml(message)}</span>
    `;

    this.toastHub.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }

  initYear() {
    const el = document.getElementById('current-year');
    if (el) el.textContent = new Date().getFullYear();
  }

  escapeHtml(str) {
    if (!str) return '';
    return str
      .toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Expose classes for window and developer console testing
if (typeof window !== 'undefined') {
  window.TruthTagDB = TruthTagDB;
  window.TruthTagVerifier = TruthTagVerifier;
  window.TruthTagApp = TruthTagApp;
}

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.truthTagApp = new TruthTagApp();
});
