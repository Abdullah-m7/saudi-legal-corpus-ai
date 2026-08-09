# Saudi Companies Law — multi-book corpus build
# Structured-first: JSON is canonical; JSONL/HTML/PDF are generated from it.
# Book One (Articles 1-34) and Book Two (Articles 35-50) build independently.

PY ?= python3
export PYTHONPATH := src:$(PYTHONPATH)

.PHONY: help data jsonl markdown validate book1-validate test html pdf build all clean \
        book2-data book2-jsonl book2-validate book2-html book2-pdf book2-build books-build \
        book3-data book3-jsonl book3-validate book3-html book3-pdf book3-build \
        book4-coverage book4-validate book4-model-check book4-coverage-check \
        book4-section1-data book4-section1-jsonl book4-section1-html book4-section1-build \
        book4-section2-data book4-section2-jsonl book4-section2-html book4-section2-build \
        book4-section3-data book4-section3-jsonl book4-section3-html book4-section3-build \
        book4-section4-data book4-section4-jsonl book4-section4-html book4-section4-build \
        book4-section5-data book4-section5-jsonl book4-section5-html book4-section5-build \
        arabic-legal-llm-data arabic-legal-llm-book4-section2-data \
        arabic-legal-llm-book4-section3-data arabic-legal-llm-book4-section4-data \
        arabic-legal-llm-book4-section5-data arabic-legal-llm-validate \
        official-english-source-extract official-english-source-validate \
        english-reference-book1-data english-reference-book1-jsonl \
        english-reference-book2-data english-reference-book2-jsonl \
        english-reference-book3-data english-reference-book3-jsonl \
        english-reference-book4-section1-data english-reference-book4-section1-jsonl \
        english-reference-book4-section2-data english-reference-book4-section2-jsonl \
        english-reference-book4-section3-data english-reference-book4-section3-jsonl \
        english-reference-book4-section4-data english-reference-book4-section4-jsonl \
        english-reference-book4-section5-data english-reference-book4-section5-jsonl \
        english-reference-validate \
        english-legal-llm-book1-data english-legal-llm-book2-data english-legal-llm-book3-data \
        english-legal-llm-book4-section1-data english-legal-llm-book4-section2-data \
        english-legal-llm-book4-section3-data english-legal-llm-book4-section4-data \
        english-legal-llm-book4-section5-data english-legal-llm-validate \
        chinese-legal-llm-book4-section1-data chinese-legal-llm-book4-section2-data \
        chinese-legal-llm-book4-section3-data chinese-legal-llm-book4-section4-data \
        chinese-legal-llm-book4-section5-data chinese-legal-llm-validate \
        official-arabic-foundation-validate official-arabic-user-provided-data \
        official-arabic-ingestion-validate official-arabic-verification-report-validate \
        official-arabic-manual-review-queue-validate official-arabic-p0-article3-review-validate \
        official-arabic-queue-p0-resolution-validate official-arabic-boe-source-provenance-validate \
        official-arabic-legal-llm-full-data official-arabic-legal-llm-full-validate \
        english-reference-full-281-data english-reference-full-281-validate \
        official-english-legal-llm-full-data official-english-legal-llm-full-validate \
        chinese-bab1-original-pdf-translation-review-data \
        chinese-bab1-original-pdf-translation-review-validate \
        chinese-all-babs-source-inventory-data chinese-all-babs-source-inventory-validate \
        chinese-internal-legal-llm-isolable-data chinese-internal-legal-llm-isolable-validate \
        chinese-internal-llm-semantic-qa-gap-plan-data \
        chinese-internal-llm-semantic-qa-gap-plan-validate \
        chinese-remediation-backlog-source-packet-plan-data \
        chinese-remediation-backlog-source-packet-plan-validate \
        chinese-remediation-batch-p0-001-validate \
        chinese-remediation-batch-p0-001-qa-validate \
        chinese-remediation-batch-p0-001-minor-fixes-validate \
        chinese-remediation-batch-p0-002-validate \
        chinese-remediation-batch-p0-002-qa-validate \
        chinese-remediation-batch-p0-003-validate \
        chinese-remediation-batch-p0-003-qa-validate \
        chinese-remediation-batch-p0-004-validate \
        chinese-remediation-batch-p0-004-qa-validate \
        chinese-remediation-batch-p0-005-validate \
        chinese-remediation-batch-p0-005-qa-validate \
        chinese-remediation-batch-p1-001-validate \
        chinese-remediation-batch-p1-001-qa-validate \
        chinese-remediation-batch-p1-002-validate \
        chinese-remediation-batch-p1-002-qa-validate \
        chinese-remediation-batch-p1-003-validate \
        chinese-remediation-batch-p1-003-qa-validate \
        chinese-remediation-batch-p1-004-validate \
        chinese-remediation-batch-p1-004-qa-validate \
        chinese-remediation-batch-p2-001-validate \
        chinese-remediation-batch-p2-001-qa-validate \
        chinese-remediation-batch-p2-002-validate \
        chinese-remediation-batch-p2-002-qa-validate \
        chinese-remediation-batch-p2-003-validate \
        chinese-remediation-batch-p2-003-qa-validate \
        chinese-remediation-batch-p2-004-validate \
        chinese-remediation-batch-p2-004-qa-validate \
        chinese-remediation-batch-p2-005-validate \
        chinese-remediation-batch-p2-005-qa-validate \
        chinese-remediation-batch-p3-conf-001-validate \
        chinese-remediation-batch-p3-conf-001-qa-validate \
        legal-corpus-factory-foundation-validate \
        repository-ux-docs-validate \
        repository-rename-readiness-validate \
        chinese-remediation-program-closure-validate \
        implementing-regulations-intake-scaffold-validate \
        implementing-regulations-listed-jsc-arabic-source-validate \
        implementing-regulations-general-arabic-source-validate \
        implementing-regulations-general-arabic-legal-llm-data \
        implementing-regulations-general-arabic-legal-llm-validate \
        implementing-regulations-listed-jsc-arabic-legal-llm-data \
        implementing-regulations-listed-jsc-arabic-legal-llm-validate \
        implementing-regulations-arabic-program-closure-data \
        implementing-regulations-arabic-program-closure-validate \
        corpus-registry-data \
        corpus-registry-validate \
        corpus-export-primary-arabic-data \
        corpus-export-primary-arabic-validate \
        corpus-local-search-validate \
        corpus-local-search-eval-validate \
        corpus-retrieval-context-pack-validate \
        corpus-retrieval-prompt-pack-validate \
        corpus-citation-support-checker-validate \
        corpus-retrieval-workflow-runner-validate \
        corpus-retrieval-demo-scenarios-validate \
        corpus-retrieval-operator-demo-pack-validate \
        pdpl-arabic-law-next-layer-validate \
        pdpl-implementing-regulation-arabic-next-layer-validate \
        pdpl-implementing-regulation-arabic-cleaned-validate \
        pdpl-implementing-regulation-arabic-verified-validate \
        pdpl-implementing-regulation-arabic-legal-llm-validate \
        pdpl-arabic-law-verified-validate \
        pdpl-arabic-law-legal-llm-validate \
        investment-law-verified-validate \
        investment-law-legal-llm-validate \
        investment-regulation-verified-validate \
        investment-regulation-legal-llm-validate \
        civil-transactions-law-verified-validate \
        civil-transactions-law-legal-llm-validate \
        corpus-unified-llm-index-validate \
        corpus-retrieval-eval-validate \
        gtpl-law-track-validate \
        gtpl-regulation-track-validate \
        labor-law-track-validate \
        labor-regulation-track-validate \
        labor-annex1-track-validate \
        labor-annex34-tracks-validate \
        labor-annex2-track-validate \
        labor-annex5-track-validate \
        evidence-law-track-validate \
        evidence-companions-tracks-validate \
        personal-status-tracks-validate \
        sharia-procedure-law-track-validate \
        sharia-procedure-regulation-track-validate \
        criminal-procedure-law-track-validate \
        criminal-procedure-regulation-track-validate \
        enforcement-law-track-validate \
        enforcement-regulation-track-validate \
        judiciary-law-track-validate \
        board-of-grievances-law-track-validate \
        law-practice-law-track-validate \
        law-practice-regulation-track-validate \
        commercial-courts-law-track-validate \
        commercial-courts-regulation-track-validate \
        bankruptcy-law-track-validate \
        bankruptcy-regulation-track-validate \
        bankruptcy-case-rules-track-validate \
        judicial-costs-law-track-validate \
        judicial-costs-regulation-track-validate \
        arbitration-law-track-validate \
        arbitration-regulation-track-validate \
        commercial-papers-law-track-validate \
        commercial-register-law-track-validate \
        trade-names-law-track-validate \
        commercial-agencies-law-track-validate \
        chambers-of-commerce-law-track-validate \
        commercial-books-law-track-validate \
        aml-law-track-validate \
        tawtheeq-law-track-validate \
        tawtheeq-regulation-track-validate \
        real-estate-registration-law-track-validate \
        real-estate-registration-regulation-track-validate \
        real-estate-mortgage-law-track-validate \
        real-estate-finance-law-track-validate \
        real-estate-units-law-track-validate \
        real-estate-units-regulation-track-validate \
        foreign-ownership-law-track-validate \
        municipal-realestate-law-track-validate \
        municipal-realestate-regulation-track-validate \
        gcc-ownership-law-track-validate \
        terrorism-law-track-validate \
        terrorism-regulation-track-validate \
        juveniles-law-track-validate \
        juveniles-regulation-track-validate \
        whistleblower-law-track-validate \
        judicial-inspection-regulation-track-validate \
        qismah-regulation-track-validate \
        sulook-regulation-track-validate \
        aawan-regulation-track-validate \
        muslaha-regulation-track-validate \
        iflas-hudud-regulation-track-validate \
        judicial-documents-regulation-track-validate \
        bankruptcy-fees-regulation-track-validate \
        enforcement-providers-regulation-track-validate \
        alimony-fund-regulation-track-validate \
        judiciary-bog-mechanism-track-validate \
        documentation-settlement-regulation-track-validate \
        mosalaha-center-regulation-track-validate \
        medical-reports-regulation-track-validate \
        marriage-non-saudi-regulation-track-validate \
        state-funded-lawyer-regulation-track-validate \
        lessor-repossession-regulation-track-validate \
        elitigation-guide-regulation-track-validate \
        judicial-training-center-guide-track-validate \
        judgment-objection-methods-regulation-track-validate \
        real-estate-expropriation-law-track-validate \
        marriage-contract-hearing-regulation-track-validate \
        anti-bribery-law-track-validate \
        basic-law-of-governance-track-validate \
        anti-cyber-crime-law-track-validate \
        anti-harassment-law-track-validate \
        anti-trafficking-law-track-validate \
        council-of-ministers-law-track-validate \
        regions-law-track-validate \
        electronic-transactions-law-track-validate \
        allegiance-commission-law-track-validate \
        shura-council-law-track-validate \
        copyright-law-track-validate \
        telecommunications-law-track-validate \
        sama-law-track-validate \
        banking-control-law-track-validate \
        capital-market-law-track-validate \
        competition-law-track-validate \
        payment-systems-law-track-validate \
        mining-investment-law-track-validate \
        trademark-law-track-validate \
        anti-concealment-law-track-validate \
        insurance-control-law-track-validate \
        ecommerce-law-track-validate \
        vat-law-track-validate \
        franchise-law-track-validate \
        civil-aviation-law-track-validate \
        anti-narcotics-law-track-validate \
        traffic-law-track-validate \
        environmental-law-track-validate \
        income-tax-law-track-validate \
        civil-service-law-track-validate \
        social-insurance-law-track-validate \
        social-insurance-legacy-law-track-validate \
        corpus-verification-tiers-validate \
        zakat-law-track-validate \
        corpus-supersession-graph-validate \
        corpus-cross-reference-graph-validate \
        corpus-glossary-validate \
        corpus-schema-manifest-validate \
        corpus-chunking-layer-validate \
        corpus-freshness-manifest-validate \
        corpus-caveat-layer-validate \
        patent-law-track-validate \
        customs-law-track-validate \
        customs-regulation-track-validate \
        anti-fraud-law-track-validate \
        finance-companies-law-track-validate \
        cooperative-health-insurance-law-track-validate \
        healthcare-professions-law-track-validate \
        finance-lease-law-track-validate \
        maritime-commercial-law-track-validate \
        gcc-anti-dumping-law-track-validate \
        accounting-auditing-law-track-validate \
        nazaha-law-track-validate \
        awqaf-law-track-validate \
        saudi-engineers-law-track-validate \
        municipal-councils-law-track-validate \
        press-law-track-validate \
        engineering-practice-law-track-validate \
        nationality-law-track-validate \
        residency-law-track-validate \
        civil-status-law-track-validate \
        food-law-track-validate \
        health-system-law-track-validate \
        domestic-labor-regulation-track-validate \
        travel-documents-law-track-validate \
        cybersecurity-authority-law-track-validate \
        cybersecurity-authority-enablers-track-validate \
        premium-residency-law-track-validate \
        travel-documents-regulation-track-validate \
        nationality-regulation-track-validate \
        health-system-regulation-track-validate \
        food-regulation-track-validate \
        electricity-law-track-validate \
        water-law-track-validate \
        vat-regulation-track-validate \
        income-tax-regulation-track-validate \
        agriculture-law-track-validate \
        competition-regulation-track-validate \
        aml-regulation-track-validate \
        patent-regulation-track-validate \
        ecommerce-regulation-track-validate \
        franchise-regulation-track-validate \
        traffic-regulation-track-validate \
        environmental-inspection-audit-reg-track-validate \
        environmental-violations-penalties-reg-track-validate \
        environmental-wildlife-hunting-reg-track-validate \
        environmental-permits-reg-track-validate \
        environmental-air-quality-reg-track-validate \
        environmental-service-providers-reg-track-validate \
        environmental-fees-reg-track-validate \
        rett-law-track-validate \
        universities-law-track-validate \
        privatization-law-track-validate \
        antiquities-heritage-law-track-validate \
        child-protection-law-track-validate \
        protection-from-abuse-law-track-validate \
        associations-ngo-law-track-validate \
        audiovisual-media-law-track-validate \
        sports-law-track-validate \
        anti-smoking-law-track-validate \
        weapons-ammunition-law-track-validate \
        prison-detention-law-track-validate \
        civil-defense-law-track-validate \
        cooperative-societies-law-track-validate \
        building-code-law-track-validate \
        product-safety-law-track-validate \
        standards-quality-law-track-validate \
        disability-rights-law-track-validate \
        tourism-law-track-validate \
        tourism-travel-services-reg-track-validate \
        hospitality-mgmt-reg-track-validate \
        hospitality-facility-reg-track-validate \
        tourist-visa-reg-track-validate \
        environmental-noise-reg-track-validate \
        environmental-protected-areas-reg-track-validate \
        environmental-emergency-response-reg-track-validate \
        product-safety-regulation-track-validate \
        handicrafts-law-track-validate \
        medical-devices-law-track-validate \
        libraries-authority-licensing-regulation-track-validate \
        theater-performing-arts-authority-licensing-regulation-track-validate \
        tourist-guidance-regulation-track-validate \
        king-saud-university-statute-track-validate \
        king-faisal-specialist-hospital-statute-track-validate \
        king-khaled-eye-hospital-statute-track-validate \
        state-property-acquisition-controls-track-validate \
        rehabilitation-and-damage-compensation-rules-track-validate \
        export-restriction-governance-statute-track-validate \
        occupational-fitness-examinations-regulation-track-validate \
        municipal-professions-crafts-licensing-regulation-track-validate \
        antifouling-systems-regulation-track-validate \
        cma-auditors-registration-rules-track-validate \
        national-risk-council-statute-track-validate \
        public-utility-markets-general-rules-track-validate \
        literature-publishing-translation-authority-statute-track-validate \
        museums-authority-statute-track-validate \
        heritage-authority-statute-track-validate \
        film-authority-statute-track-validate \
        libraries-authority-statute-track-validate \
        architecture-design-authority-statute-track-validate \
        music-authority-statute-track-validate \
        theater-performing-arts-authority-statute-track-validate \
        visual-arts-authority-statute-track-validate \
        culinary-arts-authority-statute-track-validate \
        fashion-authority-statute-track-validate \
        vehicle-periodic-inspection-statute-track-validate \
        public-transport-users-rights-regulation-track-validate \
        sez-cloud-computing-regulation-track-validate \
        alula-royal-commission-violations-committees-rules-track-validate \
        nonprofit-center-supervisory-bodies-relations-regulation-track-validate \
        saudi-yachts-regulation-track-validate \
        zakat-tax-accounting-services-rules-track-validate \
        national-emergency-management-authority-statute-track-validate \
        riyadh-biotechnology-center-statute-track-validate \
        digital-government-authority-statute-track-validate \
        real-estate-development-fund-law-track-validate \
        building-code-inspection-bodies-regulation-track-validate \
        accounting-services-rules-track-validate \
        king-salman-arabic-language-academy-statute-track-validate \
        biological-weapons-convention-regulation-track-validate \
        national-infrastructure-fund-law-track-validate \
        public-auction-sale-rules-track-validate \
        riyadh-nonprofit-foundation-statute-track-validate \
        state-property-allocation-recovery-controls-track-validate \
        government-foreign-property-lease-controls-track-validate \
        chemicals-management-regulation-track-validate \
        trustees-experts-fees-rules-track-validate \
        metrology-calibration-regulation-track-validate \
        financial-academy-statute-track-validate \
        accredited-valuers-fellowship-rules-track-validate \
        national-institute-educational-professional-development-statute-track-validate \
        hrdf-support-violations-regulation-track-validate \
        agricultural-development-fund-law-track-validate \
        baha-strategic-office-statute-track-validate \
        crafts-professions-heads-elections-regulation-track-validate \
        cruise-ships-controls-track-validate \
        cultural-development-fund-law-track-validate \
        digital-content-council-statute-track-validate \
        energy-allocation-regulation-track-validate \
        enterprise-size-measurement-rules-track-validate \
        final-clearing-collateral-regulation-track-validate \
        food-security-authority-statute-track-validate \
        general-irrigation-corporation-statute-track-validate \
        general-roads-authority-statute-track-validate \
        government-property-allocation-transfer-controls-track-validate \
        government-resource-systems-center-statute-track-validate \
        high-industrial-security-authority-statute-track-validate \
        industrial-mining-consultancy-rules-track-validate \
        jazan-strategic-office-statute-track-validate \
        job-seeker-allowance-statute-track-validate \
        jouf-strategic-office-statute-track-validate \
        kacare-statute-track-validate \
        kacst-statute-track-validate \
        king-abdullah-language-planning-center-statute-track-validate \
        marina-design-operation-controls-track-validate \
        maritime-travel-ticket-sales-regulation-track-validate \
        media-regulation-authority-statute-track-validate \
        municipal-licensing-procedures-regulation-track-validate \
        national-curriculum-center-statute-track-validate \
        national-health-research-institute-statute-track-validate \
        national-inspection-control-center-statute-track-validate \
        national-transport-safety-center-statute-track-validate \
        nonprofit-beneficial-owner-rules-track-validate \
        nonprofit-sector-development-center-statute-track-validate \
        northern-borders-strategic-office-statute-track-validate \
        occupational-safety-health-council-statute-track-validate \
        palms-dates-center-statute-track-validate \
        prince-mohammed-bin-salman-park-statute-track-validate \
        private-entity-client-data-transfer-regulation-track-validate \
        public-health-authority-statute-track-validate \
        public-utility-market-facilities-controls-track-validate \
        rdi-authority-statute-track-validate \
        real-estate-transaction-tax-regulation-track-validate \
        red-crescent-emblem-law-track-validate \
        red-sea-coral-turtles-authority-statute-track-validate \
        regional-headquarters-tax-rules-track-validate \
        royal-institute-traditional-arts-statute-track-validate \
        safe-manning-regulation-track-validate \
        saudi-auditors-accountants-authority-statute-track-validate \
        saudi-press-agency-statute-track-validate \
        saudi-red-sea-authority-statute-track-validate \
        saudi-space-agency-statute-track-validate \
        saudi-tourism-authority-statute-track-validate \
        saudi-water-authority-statute-track-validate \
        ship-safety-management-regulation-track-validate \
        sme-bank-law-track-validate \
        state-property-authority-statute-track-validate \
        two-holy-mosques-authority-statute-track-validate \
        visiting-yachts-controls-track-validate \
        waqf-investment-portfolios-regulation-track-validate \
        white-land-fees-executive-regulation-track-validate \
        wildlife-trade-regulation-track-validate \
        zatca-statute-track-validate \
        arabian-horse-regulation-track-validate \
        classification-societies-authorisation-regulation-track-validate \
        community-funds-rules-track-validate \
        competencies-contractors-program-rules-track-validate \
        conformity-models-general-regulation-track-validate \
        continuing-professional-education-rules-track-validate \
        dry-gas-tankers-technical-regulation-track-validate \
        electromagnetic-compatibility-technical-regulation-track-validate \
        environmental-rehabilitation-contaminated-sites-regulation-track-validate \
        explosive-atmospheres-equipment-technical-regulation-track-validate \
        foreign-investment-securities-rules-track-validate \
        government-allocation-objections-committee-rules-track-validate \
        hazardous-substances-electrical-equipment-regulation-track-validate \
        jewellery-accessories-technical-regulation-track-validate \
        kacaah-horse-disposal-regulation-track-validate \
        king-abdulaziz-reserve-beekeeping-controls-track-validate \
        king-abdulaziz-reserve-tourism-permits-controls-track-validate \
        land-customs-storage-fees-controls-track-validate \
        leather-products-technical-regulation-track-validate \
        makkah-holy-sites-transport-center-regulation-track-validate \
        marina-bunkering-controls-track-validate \
        maritime-education-training-accreditation-regulation-track-validate \
        maritime-service-record-regulation-track-validate \
        maritime-tour-operator-regulation-track-validate \
        maritime-tourism-agent-controls-track-validate \
        maritime-tourism-craft-classification-controls-track-validate \
        medical-referrals-center-statute-track-validate \
        ozone-depleting-substances-regulation-track-validate \
        paper-cardboard-technical-regulation-track-validate \
        public-agencies-staff-provisions-rules-track-validate \
        real-estate-consultancy-analytics-regulation-track-validate \
        real-estate-contributions-escrow-controls-track-validate \
        real-estate-market-analysis-controls-track-validate \
        returned-goods-customs-exemption-controls-track-validate \
        riyadh-infrastructure-projects-compliance-controls-track-validate \
        sarah-sudairi-womens-studies-center-statute-track-validate \
        sedimentary-shelf-well-drilling-permits-controls-track-validate \
        service-centers-fuel-stations-committee-rules-track-validate \
        shareek-program-center-statute-track-validate \
        special-use-vehicle-equipment-technical-regulation-track-validate \
        superyacht-chartering-controls-track-validate \
        tobacco-products-submission-fees-regulation-track-validate \
        tourist-destinations-regulation-track-validate \
        two-holy-mosques-religious-affairs-presidency-statute-track-validate \
        unesco-national-commission-statute-track-validate \
        used-imported-vehicles-technical-regulation-track-validate \
        vegetation-cover-desertification-regulation-track-validate \
        wheat-seasonal-fodder-cultivation-controls-track-validate \
        zakat-tax-dispute-settlement-committees-rules-track-validate \
        accredited-valuers-implementing-regulation-track-validate \
        administrative-judicial-council-bylaw-track-validate \
        antiquities-inspection-violations-regulation-track-validate \
        antiquities-museums-fund-regulation-track-validate \
        bankruptcy-information-documents-regulation-track-validate \
        bankruptcy-trustees-experts-rules-track-validate \
        bog-enforcement-service-providers-controls-track-validate \
        bog-judicial-inspection-regulation-track-validate \
        building-code-violations-classification-regulation-track-validate \
        capital-market-conduct-regulation-track-validate \
        capital-market-institutions-regulation-track-validate \
        capital-market-whistleblowing-regulation-track-validate \
        chambers-commerce-committees-regulation-track-validate \
        coastal-tourism-craft-classification-regulation-track-validate \
        companies-law-implementing-regulation-track-validate \
        contractors-classification-regulation-track-validate \
        copyright-law-2026-track-validate \
        copyright-law-implementing-regulation-track-validate \
        corporate-governance-regulation-track-validate \
        disability-rights-violations-committee-rules-track-validate \
        donations-collection-law-track-validate \
        economic-cities-marketing-names-controls-track-validate \
        electricity-violations-regulation-track-validate \
        excavation-permits-regulation-track-validate \
        extremism-countering-center-statute-track-validate \
        financial-advisory-profession-rules-track-validate \
        foreign-law-firms-licensing-regulation-track-validate \
        foreign-university-branches-regulation-track-validate \
        franchise-brokerage-controls-track-validate \
        gcc-registered-vehicles-stay-controls-track-validate \
        geographical-indications-protection-law-track-validate \
        government-foreign-property-lease-controls-2023-track-validate \
        government-health-practitioners-private-work-controls-track-validate \
        ict-devices-technical-regulation-track-validate \
        investment-accounts-instructions-track-validate \
        judicial-service-conflict-of-interest-rules-track-validate \
        juvenile-homes-regulation-track-validate \
        light-goods-road-transport-regulation-track-validate \
        listed-jsc-companies-regulation-track-validate \
        marine-coastal-environment-regulation-track-validate \
        ministry-of-investment-statute-track-validate \
        national-health-insurance-center-statute-track-validate \
        navigation-licence-work-permit-regulation-track-validate \
        nazaha-criminal-procedure-powers-regulation-track-validate \
        nonprofit-governance-rules-track-validate \
        nonprofit-zakat-exemption-rules-track-validate \
        personal-data-transfer-abroad-regulation-track-validate \
        pharmaceutical-herbal-establishments-regulation-track-validate \
        postal-law-regulation-track-validate \
        premium-residency-center-statute-track-validate \
        private-schools-tuition-controls-track-validate \
        public-facility-names-rules-track-validate \
        reconciliation-committees-regulation-track-validate \
        regional-headquarters-procurement-controls-track-validate \
        regional-tourism-development-councils-statute-track-validate \
        residential-commercial-gas-network-regulation-track-validate \
        riyadh-arts-university-statute-track-validate \
        riyadh-sez-center-statute-track-validate \
        saudi-culture-memory-center-statute-track-validate \
        security-cameras-law-regulation-track-validate \
        sez-companies-register-rules-track-validate \
        sez-companies-rules-track-validate \
        sez-trade-names-rules-track-validate \
        shariah-governance-capital-market-instructions-track-validate \
        simplified-investment-funds-instructions-track-validate \
        social-impact-investment-rules-track-validate \
        temporary-work-visas-regulation-track-validate \
        tourism-violations-committee-regulation-track-validate \
        violations-penalties-regulation-track-validate \
        waqf-establishment-donations-regulation-track-validate \
        waqf-owned-taxpayer-zakat-rules-track-validate \
        water-efficiency-center-statute-track-validate \
        water-electricity-regulatory-authority-statute-track-validate \
        real-estate-advertising-controls-track-validate \
        king-abdulaziz-quality-award-statute-track-validate \
        estimated-assessment-zakat-rules-track-validate \
        anti-concealment-status-correction-regulation-track-validate \
        state-realestate-monitoring-encroachment-rules-track-validate \
        heavy-equipment-regulation-center-statute-track-validate \
        electricity-tariff-technical-controls-track-validate \
        private-training-executive-rules-track-validate \
        trade-agreements-governance-mechanism-track-validate \
        crime-disclosure-financial-rewards-rules-track-validate \
        global-tourism-academy-statute-track-validate \
        development-authorities-support-center-statute-track-validate \
        licensed-realestate-developers-rules-track-validate \
        mahd-sports-academy-statute-track-validate \
        investment-promotion-authority-statute-track-validate \
        uqn-staff-transfer-rules-track-validate \
        alahsa-development-authority-statute-track-validate \
        ipo-book-building-allocation-instructions-track-validate \
        service-suspension-controls-track-validate \
        riyadh-infrastructure-projects-center-statute-track-validate \
        accounting-services-corrective-mechanism-track-validate \
        investment-council-statute-track-validate \
        board-committee-remuneration-controls-track-validate \
        jeddah-development-authority-statute-track-validate \
        esports-authority-statute-track-validate \
        national-place-names-in-commercial-names-controls-track-validate \
        temporary-camel-auctions-controls-track-validate \
        state-realestate-nonprofit-allocation-controls-track-validate \
        corruption-financial-settlements-rules-track-validate \
        government-vehicle-purchase-lease-controls-track-validate \
        official-travel-class-rules-track-validate \
        private-healthcare-purchasing-mechanism-track-validate \
        distinguished-competencies-incentive-controls-track-validate \
        secondary-data-use-general-rules-track-validate \
        arabic-calligraphy-center-statute-track-validate \
        treaty-brazil-visit-visas-track-validate \
        treaty-aircraft-seizure-supplementary-protocol-track-validate \
        treaty-unwto-cooperation-track-validate \
        treaty-chad-general-cooperation-track-validate \
        treaty-gcc-payment-systems-linkage-track-validate \
        treaty-regional-technical-cooperation-protocol-track-validate \
        treaty-bahrain-customs-cooperation-track-validate \
        treaty-taipei-economic-cultural-office-track-validate \
        treaty-iraq-double-taxation-track-validate \
        treaty-rwanda-general-cooperation-track-validate \
        treaty-iata-headquarters-track-validate \
        treaty-ifad-headquarters-track-validate \
        state-revenue-law-1448-track-validate \
        motorcycle-freight-transport-regulation-track-validate \
        gcc-jointly-owned-property-rules-track-validate \
        real-estate-exchange-transfer-mechanism-track-validate \
        sez-economic-substance-regulation-track-validate \
        treaty-gcc-wildlife-conservation-track-validate \
        treaty-unwto-elearning-capacity-track-validate \
        treaty-qatar-air-services-track-validate \
        treaty-pakistan-transfer-of-sentenced-persons-track-validate \
        treaty-unccd-secretariat-cooperation-track-validate \
        treaty-cameroon-general-cooperation-track-validate \
        treaty-azerbaijan-customs-assistance-track-validate \
        treaty-south-sudan-general-cooperation-track-validate \
        treaty-greece-maritime-transport-track-validate \
        treaty-hungary-air-services-track-validate \
        treaty-iraq-maritime-transport-track-validate \
        treaty-albania-driving-licences-track-validate \
        treaty-bangladesh-customs-assistance-track-validate \
        treaty-iala-establishment-track-validate \
        treaty-ghana-air-services-track-validate \
        treaty-guyana-air-services-track-validate \
        treaty-djibouti-maritime-transport-track-validate \
        treaty-czechia-air-services-track-validate \
        treaty-dco-headquarters-track-validate \
        treaty-nepal-general-cooperation-track-validate \
        treaty-arab-road-passenger-transport-track-validate \
        treaty-uzbekistan-energy-cooperation-track-validate \
        treaty-arab-anti-human-cloning-track-validate \
        treaty-latvia-economic-cooperation-track-validate \
        treaty-honduras-general-cooperation-track-validate \
        treaty-estonia-general-cooperation-track-validate \
        treaty-cyprus-general-cooperation-track-validate \
        treaty-slovakia-general-cooperation-track-validate \
        treaty-slovenia-general-cooperation-track-validate \
        occupational-safety-health-national-policy-track-validate \
        spending-efficiency-authority-statute-track-validate \
        realestate-platform-licensing-criteria-track-validate \
        administrative-violations-drafting-guide-track-validate \
        fresh-produce-import-controls-track-validate \
        direct-finance-investment-funds-instructions-track-validate \
        public-transport-projects-framework-track-validate \
        intracity-bus-transport-licensing-track-validate \
        narcotics-schedules-general-provisions-track-validate \
        listed-companies-accumulated-losses-instructions-track-validate \
        charitable-donations-executive-instructions-track-validate \
        railway-independent-consultant-guide-track-validate \
        nazaha-military-personnel-statute-track-validate \
        self-consumption-renewable-energy-framework-track-validate \
        offplan-engineering-consultants-qualification-track-validate \
        civil-aviation-economic-policy-track-validate \
        aquaculture-national-policies-guide-track-validate \
        gcc-financial-products-cross-registration-framework-track-validate \
        animal-health-guide-track-validate \
        abattoirs-meat-inspection-guide-track-validate \
        rural-livestock-husbandry-guide-track-validate \
        vehicle-damage-assessment-standards-track-validate \
        public-entities-governance-guide-track-validate \
        public-transport-users-rights-enforcement-guide-track-validate \
        land-transport-training-centers-accreditation-track-validate \
        arabic-language-national-policy-track-validate \
        gcc-healthcare-waste-management-system-track-validate \
        offplan-developer-technical-financial-qualification-track-validate \
        hydrogen-vehicles-technical-regulation-track-validate \
        cableway-installations-technical-regulation-track-validate \
        bog-enforcement-implementing-regulation-track-validate \
        administrative-entities-enforcement-request-procedures-track-validate \
        cloud-computing-electricity-tariff-executive-rules-track-validate \
        open-field-vegetable-crops-export-conditions-track-validate \
        mobile-generation-electricity-service-rules-track-validate \
        guaranteed-standards-guide-track-validate \
        heavy-equipment-safety-inspection-bodies-accreditation-rules-track-validate \
        emergency-orders-annulment-claims-rules-track-validate \
        hague-apostille-convention-track-validate \
        arab-states-transit-transport-agreement-track-validate \
        copyright-protection-implementing-regulation-track-validate \
        real-estate-development-fund-implementing-regulation-track-validate \
        experimental-activities-regulation-track-validate \
        visiting-private-yachts-regulation-track-validate \
        cruise-ships-regulation-track-validate \
        securities-offering-rules-track-validate \
        superyacht-chartering-regulation-track-validate \
        utility-benefit-loss-compensation-regulation-track-validate \
        repair-cost-compensation-estimation-controls-track-validate \
        museums-authority-licensing-regulation-track-validate \
        heritage-authority-licensing-regulation-track-validate \
        literature-publishing-translation-authority-licensing-regulation-track-validate \
        film-authority-licensing-regulation-track-validate \
        fashion-authority-licensing-regulation-track-validate \
        music-authority-licensing-regulation-track-validate \
        culinary-arts-authority-licensing-regulation-track-validate \
        architecture-design-authority-licensing-regulation-track-validate \
        visual-arts-authority-licensing-regulation-track-validate \
        tourism-consultancy-regulation-track-validate \
        tourism-activity-inspection-regulation-track-validate \
        duty-free-markets-rules-track-validate \
        driving-schools-regulation-track-validate \
        railway-violations-committee-rules-track-validate \
        public-transport-users-rights-mechanism-track-validate \
        gcc-pesticides-regulation-track-validate \
        military-industries-rnd-regulation-track-validate \
        international-bus-transport-regulation-track-validate \
        vehicle-periodic-inspection-regulation-track-validate \
        health-specialties-membership-regulation-track-validate \
        disability-social-programs-regulation-track-validate \
        vehicle-damage-assessment-rules-track-validate \
        tourist-accommodation-facilities-regulation-track-validate \
        ngo-council-regulation-track-validate \
        health-holding-company-statute-track-validate \
        family-funds-rules-track-validate \
        airports-economic-regulation-track-validate \
        valuation-profession-conduct-rules-track-validate \
        nazara-works-regulation-track-validate \
        ballast-water-regulation-track-validate \
        sez-kaec-regulation-track-validate \
        sez-jazan-regulation-track-validate \
        sez-raskhair-regulation-track-validate \
        charitable-societies-council-regulation-track-validate \
        customs-procedures-controls-track-validate \
        social-security-regulation-track-validate \
        revenue-sharing-rules-track-validate \
        freight-broker-logistics-regulation-track-validate \
        property-ownership-committees-rules-track-validate \
        disability-nongov-social-facilities-regulation-track-validate \
        free-zone-employees-treatment-rules-track-validate \
        inspection-control-seizure-rules-track-validate \
        ip-services-licensing-rules-track-validate \
        deposit-zones-rules-track-validate \
        air-transport-services-economic-regulation-track-validate \
        privatization-governing-rules-track-validate \
        ground-handling-air-cargo-economic-regulation-track-validate \
        museums-regulation-track-validate \
        private-universities-regulation-track-validate \
        gcc-road-transport-law-track-validate \
        marpol-regulation-track-validate \
        securities-disputes-rules-track-validate \
        state-realestate-disposal-regulation-track-validate \
        securities-depository-markets-regulation-track-validate \
        capital-adequacy-rules-track-validate \
        mergers-acquisitions-regulation-track-validate \
        taxi-activity-regulation-track-validate \
        zakat-tax-customs-committees-rules-track-validate \
        official-communications-records-regulation-track-validate \
        housing-support-regulation-track-validate \
        special-purpose-entities-rules-track-validate \
        medical-devices-regulation-track-validate \
        financial-institutions-resolution-law-track-validate \
        trade-remedies-law-track-validate \
        trade-remedies-regulation-track-validate \
        financial-fraud-law-track-validate \
        state-property-lease-law-track-validate \
        state-property-lease-regulation-track-validate \
        job-discipline-law-track-validate \
        statistics-law-track-validate \
        anti-begging-law-track-validate \
        security-cameras-law-track-validate \
        antiquities-heritage-regulation-track-validate \
        meteorology-law-track-validate \
        handicrafts-regulation-track-validate \
        donations-collection-regulation-track-validate \
        falcon-center-statute-track-validate \
        geographical-indications-regulation-track-validate \
        vacant-properties-fees-regulation-track-validate \
        waqf-investment-products-regulation-track-validate \
        insurance-disputes-committees-rules-track-validate \
        entertainment-activities-law-track-validate \
        standards-quality-regulation-track-validate \
        disability-rights-regulation-track-validate \
        anti-smoking-regulation-track-validate \
        general-education-law-track-validate \
        credit-information-law-track-validate \
        real-estate-brokerage-law-track-validate \
        state-revenue-law-track-validate \
        etec-law-track-validate \
        einvoicing-regulation-track-validate \
        pdpl-cross-border-transfer-regulation-track-validate \
        sdaia-organizational-arrangements-track-validate \
        trade-names-regulation-track-validate \
        commercial-agencies-regulation-track-validate \
        accounting-auditing-regulation-track-validate \
        commercial-register-regulation-track-validate \
        real-estate-brokerage-regulation-track-validate \
        foreign-ownership-regulation-track-validate \
        anti-fraud-regulation-track-validate \
        rett-regulation-track-validate \
        anti-narcotics-regulation-track-validate \
        anti-concealment-regulation-track-validate \
        privatization-regulation-track-validate \
        chambers-of-commerce-regulation-track-validate \
        state-revenue-regulation-track-validate \
        weapons-ammunition-regulation-track-validate \
        engineering-practice-regulation-track-validate \
        allegiance-commission-regulation-track-validate \
        social-insurance-regulation-track-validate \
        saudi-engineers-regulation-track-validate \
        child-protection-regulation-track-validate \
        whistleblower-regulation-track-validate \
        social-insurance-legacy-regulation-track-validate \
        protection-from-abuse-regulation-track-validate \
        healthcare-professions-regulation-track-validate \
        shura-council-internal-regulation-track-validate \
        civil-service-regulation-track-validate \
        associations-ngo-regulation-track-validate \
        electronic-transactions-regulation-track-validate \
        electricity-regulation-track-validate \
        maritime-commercial-regulation-track-validate \
        agriculture-regulation-track-validate \
        civil-defense-regulation-track-validate \
        premium-residency-regulation-track-validate \
        water-regulation-track-validate \
        press-regulation-track-validate \
        building-code-regulation-track-validate \
        telecommunications-regulation-track-validate \
        credit-information-regulation-track-validate \
        payment-systems-regulation-track-validate \
        banking-control-regulation-track-validate \
        finance-companies-regulation-track-validate \
        finance-lease-regulation-track-validate \
        cooperative-societies-regulation-track-validate \
        bog-enforcement-law-track-validate \
        public-prosecution-law-track-validate \
        elderly-care-law-track-validate \
        elderly-care-regulation-track-validate \
        private-schools-regulation-track-validate \
        foreign-schools-regulation-track-validate \
        postal-law-track-validate \
        cma-corporate-governance-regulation-track-validate \
        tvtc-organizational-statute-track-validate \
        waste-management-law-track-validate \
        fisheries-law-track-validate \
        debt-collection-regulation-track-validate \
        insurance-authority-statute-track-validate \
        bnpl-regulation-track-validate \
        offplan-sale-law-track-validate \
        contractors-classification-law-track-validate \
        real-estate-contributions-law-track-validate \
        accredited-valuers-law-track-validate \
        white-land-fees-law-track-validate \
        frequency-spectrum-regulation-track-validate \
        mental-health-law-track-validate \
        organ-donation-law-track-validate \
        private-healthcare-institutions-law-track-validate \
        high-risk-professions-regulation-track-validate \
        osh-service-providers-regulation-track-validate \
        rega-organizational-statute-track-validate \
        offplan-sale-implementing-regulation-track-validate \
        real-estate-finance-implementing-regulation-track-validate \
        real-estate-contributions-implementing-regulation-track-validate \
        landlord-tenant-relationship-regulation-track-validate \
        real-estate-marketing-advertising-regulation-track-validate \
        real-estate-auctions-regulation-track-validate \
        petroleum-petrochemical-materials-law-track-validate \
        dry-gas-lpg-distribution-law-track-validate \
        energy-supplies-system-track-validate \
        mining-investment-implementing-regulation-track-validate \
        pharmaceutical-establishments-law-track-validate \
        seized-confiscated-funds-management-system-track-validate \
        nca-cybersecurity-violations-investigation-rules-track-validate \
        nca-cybersecurity-violations-reporting-rules-track-validate \
        cst-organizational-statute-track-validate \
        railway-law-track-validate \
        railway-law-implementing-regulation-track-validate \
        road-transport-law-track-validate \
        gaca-organizational-statute-track-validate \
        tga-organizational-statute-track-validate \
        mawani-organizational-statute-track-validate \
        hajj-umrah-external-pilgrims-law-track-validate \
        aviation-passenger-rights-regulation-track-validate \
        qa-gate

help:
	@echo "Book One (default) targets:"
	@echo "  make data          - regenerate Book One canonical JSON + coverage"
	@echo "  make jsonl         - build Book One data/articles/*.jsonl"
	@echo "  make markdown      - render Book One content/{ar,zh,bilingual} Markdown"
	@echo "  make validate      - validate Book One (schema + QA)"
	@echo "  make book1-validate- alias for 'make validate'"
	@echo "  make html          - render dist/book1.html (searchable canonical text)"
	@echo "  make pdf           - render dist/book1.pdf via WeasyPrint (optional)"
	@echo "  make build         - Book One: jsonl + markdown + validate + html (+ pdf)"
	@echo "  make test          - run the full pytest suite (both books)"
	@echo "  make all           - data + build + test"
	@echo ""
	@echo "Book Two (شركة التضامن / 无限公司) targets:"
	@echo "  make book2-data    - regenerate Book Two canonical JSON + coverage"
	@echo "  make book2-jsonl   - build Book Two data/articles/*.jsonl"
	@echo "  make book2-validate- validate Book Two (schema + QA)"
	@echo "  make book2-html    - render dist/book2.html + Book Two Markdown"
	@echo "  make book2-pdf     - render dist/book2.pdf via WeasyPrint (optional)"
	@echo "  make book2-build   - Book Two: jsonl + validate + html (+ pdf)"
	@echo ""
	@echo "Book Three (شركة التوصية البسيطة / 两合公司) targets:"
	@echo "  make book3-data    - regenerate Book Three canonical JSON + coverage"
	@echo "  make book3-jsonl   - build Book Three data/articles/*.jsonl"
	@echo "  make book3-validate- validate Book Three (schema + QA)"
	@echo "  make book3-html    - render dist/book3.html + Book Three Markdown"
	@echo "  make book3-pdf     - render dist/book3.pdf via WeasyPrint (optional)"
	@echo "  make book3-build   - Book Three: jsonl + validate + html (+ pdf)"
	@echo "  make books-build   - build all books"
	@echo ""
	@echo "  make clean         - remove generated dist/ artifacts and JSONL files"
	@echo ""
	@echo "PDPL Arabic Law targets:"
	@echo "  make pdpl-arabic-law-next-layer-validate - validate Arabic PDPL law next-layer records"

# -- Book One (default; unchanged behaviour) -------------------------------
data:
	$(PY) scripts/gen_articles.py

jsonl:
	$(PY) scripts/build_jsonl.py

markdown:
	$(PY) scripts/render_markdown.py

validate:
	$(PY) scripts/validate_corpus.py --book 1

book1-validate: validate

test:
	$(PY) -m pytest

html:
	$(PY) scripts/render_book_html.py

pdf: html
	-$(PY) scripts/render_pdf_weasyprint.py

build: jsonl markdown validate html
	-$(PY) scripts/render_pdf_weasyprint.py
	@echo "build complete: dist/book1.html (canonical text) + dist/book1.pdf (if WeasyPrint present)"

all: data build test

# -- Book Two --------------------------------------------------------------
book2-data:
	$(PY) scripts/gen_book2_articles.py

book2-jsonl:
	$(PY) scripts/build_book2_jsonl.py

book2-validate:
	$(PY) scripts/validate_corpus.py --book 2

book2-html:
	$(PY) scripts/render_book2_html.py

book2-pdf: book2-html
	-$(PY) scripts/render_book2_pdf_weasyprint.py

book2-build: book2-jsonl book2-validate book2-html
	-$(PY) scripts/render_book2_pdf_weasyprint.py
	@echo "book2 build complete: dist/book2.html (canonical text) + dist/book2.pdf (if WeasyPrint present)"

# -- Book Three ------------------------------------------------------------
book3-data:
	$(PY) scripts/gen_book3_articles.py

book3-jsonl:
	$(PY) scripts/build_book3_jsonl.py

book3-validate:
	$(PY) scripts/validate_corpus.py --book 3

book3-html:
	$(PY) scripts/render_book3_html.py

book3-pdf: book3-html
	-$(PY) scripts/render_book3_pdf_weasyprint.py

book3-build: book3-jsonl book3-validate book3-html
	-$(PY) scripts/render_book3_pdf_weasyprint.py
	@echo "book3 build complete: dist/book3.html (canonical text) + dist/book3.pdf (if WeasyPrint present)"

books-build: build book2-build book3-build

# -- Book Four (model 1b — infrastructure stage; NO content build) ----------
book4-coverage:
	$(PY) scripts/gen_book4_coverage.py

book4-validate:
	$(PY) scripts/validate_corpus.py --book 4

# Convenience aliases (same infrastructure validation; no content is built).
book4-model-check: book4-validate
book4-coverage-check: book4-validate

# -- Book Four Section 1 (provisions for explicit articles 58,59,60,66) ------
book4-section1-data:
	$(PY) scripts/gen_book4_section1_provisions.py

book4-section1-jsonl:
	$(PY) scripts/build_book4_section1_jsonl.py

book4-section1-html:
	$(PY) scripts/render_book4_section1_html.py

book4-section1-build: book4-section1-data book4-section1-jsonl book4-validate book4-section1-html
	@echo "book4 section1 build complete: provisions (58,59,60,66) + section HTML (NOT full Book Four)"

# -- Book Four Section 2 (provisions for explicit articles 67,68,71,72,75,77) --
book4-section2-data:
	$(PY) scripts/gen_book4_section2_provisions.py

book4-section2-jsonl:
	$(PY) scripts/build_book4_section2_jsonl.py

book4-section2-html:
	$(PY) scripts/render_book4_section2_html.py

book4-section2-build: book4-section2-data book4-section2-jsonl book4-validate book4-section2-html
	@echo "book4 section2 build complete: provisions (67,68,71,72,75,77) + section HTML (NOT full Book Four)"

# -- Book Four Section 3 (provisions for explicit articles 85,87,92,93,99,101,102) --
book4-section3-data:
	$(PY) scripts/gen_book4_section3_provisions.py

book4-section3-jsonl:
	$(PY) scripts/build_book4_section3_jsonl.py

book4-section3-html:
	$(PY) scripts/render_book4_section3_html.py

book4-section3-build: book4-section3-data book4-section3-jsonl book4-validate book4-section3-html
	@echo "book4 section3 build complete: provisions (85,87,92,93,99,101,102) + section HTML (NOT full Book Four)"

# -- Book Four Section 4 (provisions for explicit articles 108,113,115,117) --
# Owner Option 1 reconciliation: Article 110 reclassified not_explicit_in_source.
book4-section4-data:
	$(PY) scripts/gen_book4_section4_provisions.py

book4-section4-jsonl:
	$(PY) scripts/build_book4_section4_jsonl.py

book4-section4-html:
	$(PY) scripts/render_book4_section4_html.py

book4-section4-build: book4-section4-data book4-section4-jsonl book4-validate book4-section4-html
	@echo "book4 section4 build complete: provisions (108,113,115,117) + section HTML (NOT full Book Four)"

# -- Book Four Section 5 (provisions for explicit articles 123,124,126,127,128,129,130,132,133) --
# Coverage matrix and source PDF agree on the explicit set (no reclassification).
book4-section5-data:
	$(PY) scripts/gen_book4_section5_provisions.py

book4-section5-jsonl:
	$(PY) scripts/build_book4_section5_jsonl.py

book4-section5-html:
	$(PY) scripts/render_book4_section5_html.py

book4-section5-build: book4-section5-data book4-section5-jsonl book4-validate book4-section5-html
	@echo "book4 section5 build complete: provisions (123,124,126,127,128,129,130,132,133) + section HTML (NOT full Book Four)"

# -- Arabic Legal LLM-ready layer (structured Arabic metadata) ---------------
arabic-legal-llm-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section1.py
	$(PY) scripts/gen_arabic_legal_llm_books1_3.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section2.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section3.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section4.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section5.py

arabic-legal-llm-book4-section2-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section2.py

arabic-legal-llm-book4-section3-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section3.py

arabic-legal-llm-book4-section4-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section4.py

arabic-legal-llm-book4-section5-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section5.py

arabic-legal-llm-validate:
	$(PY) scripts/validate_arabic_legal_llm.py

# -- Official English guidance source (intake + provenance + planning only) --
official-english-source-extract:
	$(PY) scripts/extract_official_english_pdf_text.py

official-english-source-validate:
	$(PY) scripts/validate_official_english_source.py

# -- Official English guidance REFERENCE layer (Book One pilot; Articles 1–34) --
# Reference/alignment text only — NOT the English Legal LLM-ready layer.
english-reference-book1-data:
	$(PY) scripts/gen_english_reference_book1.py

# The JSONL is produced together with the JSON by the generator above.
english-reference-book1-jsonl: english-reference-book1-data

# Books Two and Three share the Book One extraction/segmentation logic.
english-reference-book2-data english-reference-book3-data:
	$(PY) scripts/gen_english_reference_books2_3.py

english-reference-book2-jsonl: english-reference-book2-data
english-reference-book3-jsonl: english-reference-book3-data

# Book Four Section 1 — model 1b provision-covered articles only (58,59,60,66).
english-reference-book4-section1-data:
	$(PY) scripts/gen_english_reference_book4_section1.py

english-reference-book4-section1-jsonl: english-reference-book4-section1-data

# Book Four Section 2 — model 1b provision-covered articles only (67,68,71,72,75,77).
english-reference-book4-section2-data:
	$(PY) scripts/gen_english_reference_book4_section2.py

english-reference-book4-section2-jsonl: english-reference-book4-section2-data

# Book Four Section 3 — model 1b provision-covered articles only (85,87,92,93,99,101,102).
# Article 100 is out of scope (exists in the English source but maps to Article 101).
english-reference-book4-section3-data:
	$(PY) scripts/gen_english_reference_book4_section3.py

english-reference-book4-section3-jsonl: english-reference-book4-section3-data

# Book Four Section 4 — model 1b provision-covered articles only (108,113,115,117).
# Article 110 is out of scope (exists in the English source but reclassified uncovered).
english-reference-book4-section4-data:
	$(PY) scripts/gen_english_reference_book4_section4.py

english-reference-book4-section4-jsonl: english-reference-book4-section4-data

# Book Four Section 5 — model 1b provision-covered articles only
# (123,124,126,127,128,129,130,132,133). Articles 134 & 135 are out of scope
# (exist in the English source but cross-reference only in the model-1b source).
english-reference-book4-section5-data:
	$(PY) scripts/gen_english_reference_book4_section5.py

english-reference-book4-section5-jsonl: english-reference-book4-section5-data

english-reference-validate:
	$(PY) scripts/validate_english_reference.py

# -- English Legal LLM-ready layer --
# legal_rule_text_en is verbatim from the English reference; no generated summaries.
# Books 1-3 backfill: one article_reference record per article (1-34 / 35-50 / 51-57).
english-legal-llm-book1-data:
	$(PY) scripts/gen_english_legal_llm_book1.py

english-legal-llm-book2-data:
	$(PY) scripts/gen_english_legal_llm_book2.py

english-legal-llm-book3-data:
	$(PY) scripts/gen_english_legal_llm_book3.py

# repo book4 Section 1 — provision-covered articles only (58,59,60,66).
english-legal-llm-book4-section1-data:
	$(PY) scripts/gen_english_legal_llm_book4_section1.py

# Book Four Section 2 — provision-covered articles only (67,68,71,72,75,77).
english-legal-llm-book4-section2-data:
	$(PY) scripts/gen_english_legal_llm_book4_section2.py

# Book Four Section 3 — provision-covered articles only (85,87,92,93,99,101,102).
english-legal-llm-book4-section3-data:
	$(PY) scripts/gen_english_legal_llm_book4_section3.py

# Book Four Section 4 — provision-covered articles only (108,113,115,117).
english-legal-llm-book4-section4-data:
	$(PY) scripts/gen_english_legal_llm_book4_section4.py

# Book Four Section 5 — provision-covered articles only (123,124,126,127,128,129,130,132,133).
english-legal-llm-book4-section5-data:
	$(PY) scripts/gen_english_legal_llm_book4_section5.py

english-legal-llm-validate:
	$(PY) scripts/validate_english_legal_llm.py

# -- Chinese Legal LLM-ready layer (PILOT: Book Four Section 1 only; 58,59,60,66) --
# legal_rule_text_zh is verbatim from each provision's chinese_translation; internal
# working translation only (Arabic governs); no new/machine translation.
chinese-legal-llm-book4-section1-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section1.py

# Book Four Section 2 — provision groups only ([67,68],[71],[72],[75],[77]).
chinese-legal-llm-book4-section2-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section2.py

# Book Four Section 3 — provision groups only ([85,87],[92,93],[99],[101],[102]).
chinese-legal-llm-book4-section3-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section3.py

# Book Four Section 4 — provision groups only ([108],[113],[115],[117]).
chinese-legal-llm-book4-section4-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section4.py

# Book Four Section 5 — provision groups only ([123,124],[126,127],[128,129,130],[132],[133]).
chinese-legal-llm-book4-section5-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section5.py

chinese-legal-llm-validate:
	$(PY) scripts/validate_chinese_legal_llm.py

# -- Official Arabic text FOUNDATION (scaffold: architecture + verification workflow) --
# Validates the scaffold only; does NOT ingest or verify official Arabic text.
official-arabic-foundation-validate:
	$(PY) scripts/validate_official_arabic_foundation.py

# -- Official Arabic USER-PROVIDED ingestion (unverified candidate; 281 article records) --
# Segments the user-provided packet into 281 records + per-article hashes. Nothing verified.
official-arabic-user-provided-data:
	$(PY) scripts/ingest_official_arabic_user_provided_text.py

official-arabic-ingestion-validate:
	$(PY) scripts/validate_official_arabic_ingestion.py

# -- Official Arabic source VERIFICATION (comparison/report only; nothing promoted) --
# compare_official_arabic_candidate_to_source.py reads the committed OCR artifact (no OCR
# engine needed) and rewrites the comparison report deterministically.
official-arabic-verification-report-validate:
	$(PY) scripts/validate_official_arabic_verification_report.py

# -- Official Arabic OCR MANUAL-REVIEW QUEUE (triage only; promotes nothing) --
# build_official_arabic_manual_review_queue.py reads the committed comparison report +
# candidate + OCR artifact (no OCR engine) and rewrites the queue deterministically.
official-arabic-manual-review-queue-validate:
	$(PY) scripts/validate_official_arabic_manual_review_queue.py

# -- Official Arabic P0 Article 3 segmentation review (triage only; promotes nothing) --
official-arabic-p0-article3-review-validate:
	$(PY) scripts/validate_official_arabic_p0_article3_review.py

# -- Official Arabic queue P0-resolution update (status only; promotes nothing) --
# update script re-runs the resolution-aware queue builder deterministically.
official-arabic-queue-p0-resolution-validate:
	$(PY) scripts/validate_official_arabic_queue_p0_resolution.py

# -- Official Arabic BOE source provenance/status correction (provenance only; verifies nothing) --
official-arabic-boe-source-provenance-validate:
	$(PY) scripts/validate_official_arabic_boe_source_provenance.py

# -- Official Arabic FULL LLM-ready layer (281 articles; exact official_text_ar; no OCR) --
official-arabic-legal-llm-full-data:
	$(PY) scripts/gen_official_arabic_legal_llm_full_281.py

official-arabic-legal-llm-full-validate:
	$(PY) scripts/validate_official_arabic_legal_llm_full_281.py

# -- Full official English BOE reference alignment (281 articles; guidance only; Arabic governs) --
english-reference-full-281-data:
	$(PY) scripts/gen_english_reference_full_281.py

english-reference-full-281-validate:
	$(PY) scripts/validate_english_reference_full_281.py

# -- Full official English Legal LLM-ready layer (281 articles; verbatim guidance text; Arabic governs) --
official-english-legal-llm-full-data:
	$(PY) scripts/gen_official_english_legal_llm_full_281.py

official-english-legal-llm-full-validate:
	$(PY) scripts/validate_official_english_legal_llm_full_281.py

# -- Chinese Bab 1 original-PDF translation review (source inventory only; no Chinese LLM-ready) --
chinese-bab1-original-pdf-translation-review-data:
	$(PY) scripts/gen_chinese_bab1_original_pdf_translation_review.py

chinese-bab1-original-pdf-translation-review-validate:
	$(PY) scripts/validate_chinese_bab1_original_pdf_translation_review.py

# -- Chinese all-Babs (1-14) source coverage inventory (source inventory only; no Chinese LLM-ready) --
chinese-all-babs-source-inventory-data:
	$(PY) scripts/gen_chinese_all_babs_source_inventory.py

chinese-all-babs-source-inventory-validate:
	$(PY) scripts/validate_chinese_all_babs_source_inventory.py

# -- Chinese internal LLM-ready candidate layer (isolable-source articles only; internal/reference) --
chinese-internal-legal-llm-isolable-data:
	$(PY) scripts/gen_chinese_internal_legal_llm_isolable_source_articles.py

chinese-internal-legal-llm-isolable-validate:
	$(PY) scripts/validate_chinese_internal_legal_llm_isolable_source_articles.py

# -- Chinese internal candidate semantic QA (189) + completion gap plan (281) (QA/plan only) --
chinese-internal-llm-semantic-qa-gap-plan-data:
	$(PY) scripts/gen_chinese_internal_llm_semantic_qa_gap_plan.py

chinese-internal-llm-semantic-qa-gap-plan-validate:
	$(PY) scripts/validate_chinese_internal_llm_semantic_qa_gap_plan.py

# -- Chinese remediation backlog + batch plan + source-packet manifest (planning only; no Chinese) --
chinese-remediation-backlog-source-packet-plan-data:
	$(PY) scripts/gen_chinese_remediation_backlog_source_packet_plan.py

chinese-remediation-backlog-source-packet-plan-validate:
	$(PY) scripts/validate_chinese_remediation_backlog_source_packet_plan.py

# -- Chinese remediation Batch P0-001 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001.py

# -- Chinese remediation Batch P0-001 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001_qa.py

# -- Chinese remediation Batch P0-001 minor fixes (Articles 61 & 74 terminology only) --
chinese-remediation-batch-p0-001-minor-fixes-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001_minor_fixes.py

# -- Chinese remediation Batch P0-002 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_002.py

# -- Chinese remediation Batch P0-002 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_002_qa.py

# -- Chinese remediation Batch P0-003 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_003.py

# -- Chinese remediation Batch P0-003 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_003_qa.py

# -- Chinese remediation Batch P0-004 (scoped internal Chinese draft; 20 articles, Babs 4/5/6; from Arabic) --
chinese-remediation-batch-p0-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_004.py

# -- Chinese remediation Batch P0-004 QA (article-by-article vs Arabic; Babs 4/5/6; review only) --
chinese-remediation-batch-p0-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_004_qa.py

# -- Chinese remediation Batch P0-005 (final P0 batch; 12 articles, Babs 7/9/10/13/14; from Arabic) --
chinese-remediation-batch-p0-005-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_005.py

# -- Chinese remediation Batch P0-005 QA (final P0 batch; article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-005-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_005_qa.py

# -- Chinese remediation Batch P1-001 (first P1 batch; 20 articles, Babs 1/2; retranslate from Arabic) --
chinese-remediation-batch-p1-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_001.py

# -- Chinese remediation Batch P1-001 QA (article-by-article vs Arabic; review only; Babs 1/2) --
chinese-remediation-batch-p1-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_001_qa.py

# -- Chinese remediation Batch P1-002 (20 articles, Babs 3/4/5/6; retranslate from Arabic) --
chinese-remediation-batch-p1-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_002.py

# -- Chinese remediation Batch P1-002 QA (article-by-article vs Arabic; review only; Babs 3/4/5/6) --
chinese-remediation-batch-p1-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_002_qa.py

# -- Chinese remediation Batch P1-003 (20 articles, Babs 6/7/8/10; retranslate from Arabic) --
chinese-remediation-batch-p1-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_003.py

# -- Chinese remediation Batch P1-003 QA (article-by-article vs Arabic; review only; Babs 6/7/8/10) --
chinese-remediation-batch-p1-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_003_qa.py

# -- Chinese remediation Batch P1-004 (16 articles, Babs 10/12/13/14; retranslate from Arabic) --
chinese-remediation-batch-p1-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_004.py

# -- Chinese remediation Batch P1-004 QA (article-by-article vs Arabic; review only; Babs 10/12/13/14) --
chinese-remediation-batch-p1-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_004_qa.py

# -- Chinese remediation Batch P2-001 (first P2 expansion batch; 20 articles, Babs 1/2/4) --
chinese-remediation-batch-p2-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_001.py

# -- Chinese remediation Batch P2-001 QA (first P2 expansion QA; review only; Babs 1/2/4) --
chinese-remediation-batch-p2-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_001_qa.py

# -- Chinese remediation Batch P2-002 (second P2 expansion batch; 20 articles, Babs 4/5/6/7) --
chinese-remediation-batch-p2-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_002.py

# -- Chinese remediation Batch P2-002 QA (second P2 expansion QA; review only; Babs 4/5/6/7) --
chinese-remediation-batch-p2-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_002_qa.py

# -- Chinese remediation Batch P2-003 (P2 expansion batch; 20 articles, Babs 7/8/9/10) --
chinese-remediation-batch-p2-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_003.py

# -- Chinese remediation Batch P2-003 QA (P2 expansion QA; review only; Babs 7/8/9/10) --
chinese-remediation-batch-p2-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_003_qa.py

# -- Chinese remediation Batch P2-004 (P2 expansion batch; 20 articles, Babs 10/11/12) --
chinese-remediation-batch-p2-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_004.py

# -- Chinese remediation Batch P2-004 QA (P2 expansion QA; review only; Babs 10/11/12) --
chinese-remediation-batch-p2-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_004_qa.py

# -- Chinese remediation Batch P2-005 (P2 expansion batch; 15 articles, Babs 12/13/14) --
chinese-remediation-batch-p2-005-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_005.py

# -- Chinese remediation Batch P2-005 QA (P2 expansion QA; review only; Babs 12/13/14) --
chinese-remediation-batch-p2-005-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_005_qa.py

# -- Chinese confirmation Batch P3-CONF-001 (final P3 confirmation batch; 18 articles, Babs 2/3; retain) --
chinese-remediation-batch-p3-conf-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p3_conf_001.py

# -- Chinese confirmation Batch P3-CONF-001 QA (final P3 confirmation QA; review only; Babs 2/3) --
chinese-remediation-batch-p3-conf-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p3_conf_001_qa.py

# -- Sovereign legal corpus factory foundation (doctrine, architecture, schemas, profile, config, seed) --
legal-corpus-factory-foundation-validate:
	$(PY) scripts/validate_legal_corpus_factory_foundation.py

# -- Repository UX / navigation docs (README top + START_HERE/STATUS/REPOSITORY_MAP/USE_CASES) --
repository-ux-docs-validate:
	$(PY) scripts/validate_repository_ux_docs.py

# -- Repository rename readiness (saudi-companies-law-ar-zh-llm -> saudi-legal-corpus-ai) --
repository-rename-readiness-validate:
	$(PY) scripts/validate_repository_rename_readiness.py

# -- Chinese remediation program closure audit (read-only; P0..P3 complete) --
chinese-remediation-program-closure-validate:
	$(PY) scripts/validate_chinese_remediation_program_closure.py

# -- Implementing regulations intake scaffold (scaffold only; no intake/translation) --
implementing-regulations-intake-scaffold-validate:
	$(PY) scripts/validate_implementing_regulations_intake_scaffold.py

# -- Listed joint-stock implementing regulation Arabic source intake (69 articles; specialized) --
implementing-regulations-listed-jsc-arabic-source-validate:
	$(PY) scripts/validate_implementing_regulations_listed_jsc_arabic_source.py

# -- General implementing regulations Arabic source intake (95 articles; 7 chapters; 4 forms) --
implementing-regulations-general-arabic-source-validate:
	$(PY) scripts/validate_implementing_regulations_general_arabic_source.py

# -- General implementing regulations Arabic Legal LLM layer (95 article records + 4 form records) --
implementing-regulations-general-arabic-legal-llm-data:
	$(PY) scripts/gen_implementing_regulations_general_arabic_legal_llm.py

implementing-regulations-general-arabic-legal-llm-validate:
	$(PY) scripts/validate_implementing_regulations_general_arabic_legal_llm.py

# -- Listed joint-stock implementing regulation Arabic Legal LLM layer (69 article records + 1 appendix) --
implementing-regulations-listed-jsc-arabic-legal-llm-data:
	$(PY) scripts/gen_implementing_regulations_listed_jsc_arabic_legal_llm.py

implementing-regulations-listed-jsc-arabic-legal-llm-validate:
	$(PY) scripts/validate_implementing_regulations_listed_jsc_arabic_legal_llm.py

# -- Implementing regulations Arabic program closure audit (read-only; covers both tracks) --
implementing-regulations-arabic-program-closure-data:
	$(PY) scripts/gen_implementing_regulations_arabic_program_closure.py

implementing-regulations-arabic-program-closure-validate:
	$(PY) scripts/validate_implementing_regulations_arabic_program_closure.py

# -- Corpus registry index foundation (canonical registry; read-only) --
corpus-registry-data:
	$(PY) scripts/gen_corpus_registry.py

corpus-registry-validate:
	$(PY) scripts/validate_corpus_registry.py

# -- Corpus export — primary Arabic governing records (v1; read-only) --
corpus-export-primary-arabic-data:
	$(PY) scripts/gen_corpus_export_primary_arabic.py

corpus-export-primary-arabic-validate:
	$(PY) scripts/validate_corpus_export_primary_arabic.py

# -- Corpus local lexical search (deterministic, offline; read-only) --
corpus-local-search-validate:
	$(PY) scripts/validate_corpus_local_search.py

corpus-local-search-smoke:
	$(PY) scripts/search_primary_arabic_export.py "الشركة" --limit 5
	@echo "---"
	$(PY) scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 5
	@echo "---"
	$(PY) scripts/search_primary_arabic_export.py "الجمعية العامة" --limit 5 --json

# -- Corpus local search evaluation fixtures (deterministic, offline) --
corpus-local-search-eval-validate:
	$(PY) scripts/validate_corpus_local_search_eval.py

# -- Corpus retrieval context pack (deterministic, offline; read-only) --
corpus-retrieval-context-pack-validate:
	$(PY) scripts/validate_retrieval_context_pack.py

corpus-retrieval-context-pack-smoke:
	$(PY) scripts/build_retrieval_context_pack.py "مجلس الإدارة" --limit 3 --format json
	@echo "---"
	$(PY) scripts/build_retrieval_context_pack.py "الجمعية العامة" --limit 3 --format markdown
	@echo "---"
	$(PY) scripts/build_retrieval_context_pack.py "التوكيل" --record-type appendix --limit 1 --format json --include-full-text

# -- Corpus retrieval prompt pack (deterministic, offline; builds prompts only) --
corpus-retrieval-prompt-pack-validate:
	$(PY) scripts/validate_retrieval_prompt_pack.py

corpus-retrieval-prompt-pack-smoke:
	$(PY) scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --limit 3 --mode evidence_brief --format json
	@echo "---"
	$(PY) scripts/build_retrieval_prompt_pack.py "الجمعية العامة" --limit 3 --mode cautious_answer_draft --format markdown
	@echo "---"
	$(PY) scripts/build_retrieval_prompt_pack.py "التوكيل" --record-type appendix --limit 1 --mode evidence_brief --format json --include-full-text

# -- Corpus citation support checker (deterministic, offline; mechanical checking only) --
corpus-citation-support-checker-validate:
	$(PY) scripts/validate_citation_support_checker.py

corpus-citation-support-checker-smoke:
	$(PY) scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --limit 3 --mode cautious_answer_draft --format json --output /tmp/_smoke_prompt_pack.json
	@echo "---"
	$(PY) -c "import json; pack=json.load(open('/tmp/_smoke_prompt_pack.json')); rid=pack['retrieved_records'][0]['export_record_id']; open('/tmp/_smoke_valid_draft.md','w').write('هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [['+'[export_record_id='+rid+']'+']].\n\nوفقًا للنظام [['+'[export_record_id='+rid+']'+']].\n')"
	$(PY) scripts/check_citation_support.py --prompt-pack /tmp/_smoke_prompt_pack.json --draft-answer-file /tmp/_smoke_valid_draft.md --require-citation-per-paragraph --format json
	@echo "---"
	$(PY) -c "open('/tmp/_smoke_invalid_draft.md','w').write('هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n')"
	$(PY) scripts/check_citation_support.py --prompt-pack /tmp/_smoke_prompt_pack.json --draft-answer-file /tmp/_smoke_invalid_draft.md --format json || true
	@rm -f /tmp/_smoke_prompt_pack.json /tmp/_smoke_valid_draft.md /tmp/_smoke_invalid_draft.md

# -- Corpus retrieval workflow runner (deterministic, offline; thin orchestration) --
corpus-retrieval-workflow-runner-validate:
	$(PY) scripts/validate_retrieval_workflow_runner.py

corpus-retrieval-workflow-runner-smoke:
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode prepare_prompt --limit 3 --prompt-mode evidence_brief --formats both --output-dir /tmp/_smoke_workflow_prep
	@echo "---"
	$(PY) -c "import json; pack=json.load(open('/tmp/_smoke_workflow_prep/prompt_pack.json')); rid=pack['retrieved_records'][0]['export_record_id']; open('/tmp/_smoke_workflow_draft.md','w').write('هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [['+'[export_record_id='+rid+']'+']].\n\nوفقًا للنظام [['+'[export_record_id='+rid+']'+']].\n')"
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode check_draft --limit 3 --prompt-mode cautious_answer_draft --draft-answer-file /tmp/_smoke_workflow_draft.md --require-citation-per-paragraph --formats both --output-dir /tmp/_smoke_workflow_check
	@rm -rf /tmp/_smoke_workflow_prep /tmp/_smoke_workflow_check /tmp/_smoke_workflow_draft.md

# -- Corpus retrieval demo scenarios (deterministic, offline; curated demo layer) --

corpus-retrieval-demo-scenarios-validate:
	$(PY) scripts/validate_retrieval_demo_scenarios.py

corpus-retrieval-demo-scenarios-smoke:
	$(PY) scripts/run_retrieval_demo_scenarios.py
	@echo "---"
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode prepare_prompt --limit 3 --prompt-mode evidence_brief --formats both --output-dir /tmp/_smoke_demo_board
	@echo "---"
	@echo "Confirming no generated workflow outputs in data/demo_scenarios/..."
	@ls data/demo_scenarios/ | grep -v "retrieval_demo_scenarios_v1.json" && echo "FAIL: unexpected files" && exit 1 || echo "OK: only scenarios JSON present"
	@rm -rf /tmp/_smoke_demo_board

# -- Corpus retrieval operator demo pack (documentation + validator only) --

corpus-retrieval-operator-demo-pack-validate:
	$(PY) scripts/validate_operator_demo_pack.py

corpus-retrieval-operator-demo-pack-smoke:
	$(PY) scripts/validate_operator_demo_pack.py
	@echo "---"
	@echo "Running demo scenarios smoke to confirm referenced commands work..."
	$(PY) scripts/run_retrieval_demo_scenarios.py
	@echo "---"
	@echo "Confirming no generated artifacts in docs/operator_demo_pack/..."
	@find docs/operator_demo_pack/ -type f ! -name "*.md" -print -quit | grep -q . && echo "FAIL: non-markdown files" && exit 1 || echo "OK: only markdown files"
	@rm -rf /tmp/corpus_demo_scenarios_*

# -- PDPL Arabic Law next-layer validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-next-layer-validate:
	$(PY) scripts/validate_pdpl_arabic_law_next_layer_records.py

# -- PDPL implementing-regulation next-layer validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-next-layer-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_next_layer_records.py

# -- PDPL implementing-regulation cleaned-text generator + validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-cleaned-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_cleaned.py

# -- PDPL implementing-regulation verified/corrected text validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-verified-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_verified.py

# -- PDPL implementing-regulation Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-legal-llm-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_legal_llm.py

# -- PDPL law verified/corrected text validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-verified-validate:
	$(PY) scripts/validate_pdpl_arabic_law_verified.py

# -- PDPL law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-legal-llm-validate:
	$(PY) scripts/validate_pdpl_arabic_law_legal_llm.py

# -- Investment Law verified text validator (dedicated target; does NOT change make validate) --
investment-law-verified-validate:
	$(PY) scripts/validate_investment_law_verified.py

# -- Investment Law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
investment-law-legal-llm-validate:
	$(PY) scripts/validate_investment_law_legal_llm.py

# -- Investment Regulations verified text validator (dedicated target; does NOT change make validate) --
investment-regulation-verified-validate:
	$(PY) scripts/validate_investment_regulation_verified.py

# -- Investment Regulations Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
investment-regulation-legal-llm-validate:
	$(PY) scripts/validate_investment_regulation_legal_llm.py

# -- Civil Transactions Law verified text validator (dedicated target; does NOT change make validate) --
civil-transactions-law-verified-validate:
	$(PY) scripts/validate_civil_transactions_law_verified.py

# -- Civil Transactions Law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
civil-transactions-law-legal-llm-validate:
	$(PY) scripts/validate_civil_transactions_law_legal_llm.py

# -- Unified cross-law LLM retrieval index generator + validator (dedicated target; does NOT change make validate) --
corpus-unified-llm-index-validate:
	$(PY) scripts/validate_corpus_unified_llm_index.py

# -- Retrieval eval pack over the unified index (dedicated target; does NOT change make validate) --
corpus-retrieval-eval-validate:
	$(PY) scripts/validate_corpus_retrieval_eval.py

# -- GTPL (M/128) track validator (dedicated target; does NOT change make validate) --
gtpl-law-track-validate:
	$(PY) scripts/validate_gtpl_law_track.py

# -- GTPL Implementing Regulation track validator (dedicated target; does NOT change make validate) --
gtpl-regulation-track-validate:
	$(PY) scripts/validate_gtpl_regulation_track.py

# -- Labor Law track validator (dedicated target; does NOT change make validate) --
labor-law-track-validate:
	$(PY) scripts/validate_labor_law_track.py

# -- Labor Regulation track validator (dedicated target; does NOT change make validate) --
labor-regulation-track-validate:
	$(PY) scripts/validate_labor_regulation_track.py

# -- Labor Annex 1 (model work organization regulation) track validator --
labor-annex1-track-validate:
	$(PY) scripts/validate_labor_annex1_track.py

# -- Labor Annex 3 + 4 tracks validator --
labor-annex34-tracks-validate:
	$(PY) scripts/validate_labor_annex34_tracks.py

# -- Labor Annex 2 (accessibility tables) track validator --
labor-annex2-track-validate:
	$(PY) scripts/validate_labor_annex2_track.py

# -- Labor Annex 5 (model contract forms) track validator --
labor-annex5-track-validate:
	$(PY) scripts/validate_labor_annex5_track.py

# -- Evidence Law track validator --
evidence-law-track-validate:
	$(PY) scripts/validate_evidence_law_track.py

# -- Evidence Law companion tracks validator (electronic rules + manuals + expertise) --
evidence-companions-tracks-validate:
	$(PY) scripts/validate_evidence_companions_tracks.py

# -- Personal Status Law + regulation tracks validator --
personal-status-tracks-validate:
	$(PY) scripts/validate_personal_status_tracks.py

# -- Law of Sharia Procedure track validator --
sharia-procedure-law-track-validate:
	$(PY) scripts/validate_sharia_procedure_law_track.py

# -- Sharia Procedure implementing-regulation track validator --
sharia-procedure-regulation-track-validate:
	$(PY) scripts/validate_sharia_procedure_regulation_track.py

# -- Law of Criminal Procedure track validator --
criminal-procedure-law-track-validate:
	$(PY) scripts/validate_criminal_procedure_law_track.py

# -- Criminal Procedure implementing-regulation track validator --
criminal-procedure-regulation-track-validate:
	$(PY) scripts/validate_criminal_procedure_regulation_track.py

# -- Enforcement Law track validator --
enforcement-law-track-validate:
	$(PY) scripts/validate_enforcement_law_track.py

# -- Enforcement implementing-regulation track validator --
enforcement-regulation-track-validate:
	$(PY) scripts/validate_enforcement_regulation_track.py

# -- Law of the Judiciary track validator --
judiciary-law-track-validate:
	$(PY) scripts/validate_judiciary_law_track.py

# -- Law of the Board of Grievances track validator --
board-of-grievances-law-track-validate:
	$(PY) scripts/validate_board_of_grievances_law_track.py

# -- Code of Law Practice track validator --
law-practice-law-track-validate:
	$(PY) scripts/validate_law_practice_law_track.py

# -- Implementing Regulation of the Code of Law Practice track validator --
law-practice-regulation-track-validate:
	$(PY) scripts/validate_law_practice_regulation_track.py

# -- Commercial Courts Law track validator --
commercial-courts-law-track-validate:
	$(PY) scripts/validate_commercial_courts_law_track.py

# -- Implementing Regulation of the Commercial Courts Law track validator --
commercial-courts-regulation-track-validate:
	$(PY) scripts/validate_commercial_courts_regulation_track.py

bankruptcy-law-track-validate:
	$(PY) scripts/validate_bankruptcy_law_track.py

bankruptcy-regulation-track-validate:
	$(PY) scripts/validate_bankruptcy_regulation_track.py

bankruptcy-case-rules-track-validate:
	$(PY) scripts/validate_bankruptcy_case_rules_track.py

judicial-costs-law-track-validate:
	$(PY) scripts/validate_judicial_costs_law_track.py

judicial-costs-regulation-track-validate:
	$(PY) scripts/validate_judicial_costs_regulation_track.py

arbitration-law-track-validate:
	$(PY) scripts/validate_arbitration_law_track.py

arbitration-regulation-track-validate:
	$(PY) scripts/validate_arbitration_regulation_track.py

commercial-papers-law-track-validate:
	$(PY) scripts/validate_commercial_papers_law_track.py

commercial-register-law-track-validate:
	$(PY) scripts/validate_commercial_register_law_track.py

trade-names-law-track-validate:
	$(PY) scripts/validate_trade_names_law_track.py

commercial-agencies-law-track-validate:
	$(PY) scripts/validate_commercial_agencies_law_track.py

chambers-of-commerce-law-track-validate:
	$(PY) scripts/validate_chambers_of_commerce_law_track.py

commercial-books-law-track-validate:
	$(PY) scripts/validate_commercial_books_law_track.py

aml-law-track-validate:
	$(PY) scripts/validate_aml_law_track.py

tawtheeq-law-track-validate:
	$(PY) scripts/validate_tawtheeq_law_track.py

tawtheeq-regulation-track-validate:
	$(PY) scripts/validate_tawtheeq_regulation_track.py

real-estate-registration-law-track-validate:
	$(PY) scripts/validate_real_estate_registration_law_track.py

real-estate-registration-regulation-track-validate:
	$(PY) scripts/validate_real_estate_registration_regulation_track.py

real-estate-mortgage-law-track-validate:
	$(PY) scripts/validate_real_estate_mortgage_law_track.py

real-estate-finance-law-track-validate:
	$(PY) scripts/validate_real_estate_finance_law_track.py

real-estate-units-law-track-validate:
	$(PY) scripts/validate_real_estate_units_law_track.py

real-estate-units-regulation-track-validate:
	$(PY) scripts/validate_real_estate_units_regulation_track.py

foreign-ownership-law-track-validate:
	$(PY) scripts/validate_foreign_ownership_law_track.py

municipal-realestate-law-track-validate:
	$(PY) scripts/validate_municipal_realestate_law_track.py

municipal-realestate-regulation-track-validate:
	$(PY) scripts/validate_municipal_realestate_regulation_track.py

gcc-ownership-law-track-validate:
	$(PY) scripts/validate_gcc_ownership_law_track.py

terrorism-law-track-validate:
	$(PY) scripts/validate_terrorism_law_track.py

terrorism-regulation-track-validate:
	$(PY) scripts/validate_terrorism_regulation_track.py

juveniles-law-track-validate:
	$(PY) scripts/validate_juveniles_law_track.py

juveniles-regulation-track-validate:
	$(PY) scripts/validate_juveniles_regulation_track.py

whistleblower-law-track-validate:
	$(PY) scripts/validate_whistleblower_law_track.py

judicial-inspection-regulation-track-validate:
	$(PY) scripts/validate_judicial_inspection_regulation_track.py

qismah-regulation-track-validate:
	$(PY) scripts/validate_qismah_regulation_track.py

sulook-regulation-track-validate:
	$(PY) scripts/validate_sulook_regulation_track.py

aawan-regulation-track-validate:
	$(PY) scripts/validate_aawan_regulation_track.py

muslaha-regulation-track-validate:
	$(PY) scripts/validate_muslaha_regulation_track.py

iflas-hudud-regulation-track-validate:
	$(PY) scripts/validate_iflas_hudud_regulation_track.py

judicial-documents-regulation-track-validate:
	$(PY) scripts/validate_judicial_documents_regulation_track.py

bankruptcy-fees-regulation-track-validate:
	$(PY) scripts/validate_bankruptcy_fees_regulation_track.py

enforcement-providers-regulation-track-validate:
	$(PY) scripts/validate_enforcement_providers_regulation_track.py

alimony-fund-regulation-track-validate:
	$(PY) scripts/validate_alimony_fund_regulation_track.py

judiciary-bog-mechanism-track-validate:
	$(PY) scripts/validate_judiciary_bog_mechanism_track.py

documentation-settlement-regulation-track-validate:
	$(PY) scripts/validate_documentation_settlement_regulation_track.py

mosalaha-center-regulation-track-validate:
	$(PY) scripts/validate_mosalaha_center_regulation_track.py

medical-reports-regulation-track-validate:
	$(PY) scripts/validate_medical_reports_regulation_track.py

marriage-non-saudi-regulation-track-validate:
	$(PY) scripts/validate_marriage_non_saudi_regulation_track.py

state-funded-lawyer-regulation-track-validate:
	$(PY) scripts/validate_state_funded_lawyer_regulation_track.py

lessor-repossession-regulation-track-validate:
	$(PY) scripts/validate_lessor_repossession_regulation_track.py

elitigation-guide-regulation-track-validate:
	$(PY) scripts/validate_elitigation_guide_regulation_track.py

judicial-training-center-guide-track-validate:
	$(PY) scripts/validate_judicial_training_center_guide_track.py

judgment-objection-methods-regulation-track-validate:
	$(PY) scripts/validate_judgment_objection_methods_regulation_track.py

real-estate-expropriation-law-track-validate:
	$(PY) scripts/validate_real_estate_expropriation_law_track.py

marriage-contract-hearing-regulation-track-validate:
	$(PY) scripts/validate_marriage_contract_hearing_regulation_track.py

anti-bribery-law-track-validate:
	$(PY) scripts/validate_anti_bribery_law_track.py

basic-law-of-governance-track-validate:
	$(PY) scripts/validate_basic_law_of_governance_track.py

anti-cyber-crime-law-track-validate:
	$(PY) scripts/validate_anti_cyber_crime_law_track.py

anti-harassment-law-track-validate:
	$(PY) scripts/validate_anti_harassment_law_track.py

anti-trafficking-law-track-validate:
	$(PY) scripts/validate_anti_trafficking_law_track.py

council-of-ministers-law-track-validate:
	$(PY) scripts/validate_council_of_ministers_law_track.py

regions-law-track-validate:
	$(PY) scripts/validate_regions_law_track.py

electronic-transactions-law-track-validate:
	$(PY) scripts/validate_electronic_transactions_law_track.py

allegiance-commission-law-track-validate:
	$(PY) scripts/validate_allegiance_commission_law_track.py

shura-council-law-track-validate:
	$(PY) scripts/validate_shura_council_law_track.py

copyright-law-track-validate:
	$(PY) scripts/validate_copyright_law_track.py

telecommunications-law-track-validate:
	$(PY) scripts/validate_telecommunications_law_track.py

sama-law-track-validate:
	$(PY) scripts/validate_sama_law_track.py

banking-control-law-track-validate:
	$(PY) scripts/validate_banking_control_law_track.py

capital-market-law-track-validate:
	$(PY) scripts/validate_capital_market_law_track.py

competition-law-track-validate:
	$(PY) scripts/validate_competition_law_track.py

payment-systems-law-track-validate:
	$(PY) scripts/validate_payment_systems_law_track.py

mining-investment-law-track-validate:
	$(PY) scripts/validate_mining_investment_law_track.py

trademark-law-track-validate:
	$(PY) scripts/validate_trademark_law_track.py

anti-concealment-law-track-validate:
	$(PY) scripts/validate_anti_concealment_law_track.py

insurance-control-law-track-validate:
	$(PY) scripts/validate_insurance_control_law_track.py

ecommerce-law-track-validate:
	$(PY) scripts/validate_ecommerce_law_track.py

vat-law-track-validate:
	$(PY) scripts/validate_vat_law_track.py

franchise-law-track-validate:
	$(PY) scripts/validate_franchise_law_track.py

civil-aviation-law-track-validate:
	$(PY) scripts/validate_civil_aviation_law_track.py

anti-narcotics-law-track-validate:
	$(PY) scripts/validate_anti_narcotics_law_track.py

traffic-law-track-validate:
	$(PY) scripts/validate_traffic_law_track.py

environmental-law-track-validate:
	$(PY) scripts/validate_environmental_law_track.py

income-tax-law-track-validate:
	$(PY) scripts/validate_income_tax_law_track.py

civil-service-law-track-validate:
	$(PY) scripts/validate_civil_service_law_track.py

social-insurance-law-track-validate:
	$(PY) scripts/validate_social_insurance_law_track.py

social-insurance-legacy-law-track-validate:
	$(PY) scripts/validate_social_insurance_legacy_law_track.py

corpus-verification-tiers-validate:
	$(PY) scripts/validate_corpus_verification_tiers.py

zakat-law-track-validate:
	$(PY) scripts/validate_zakat_law_track.py

corpus-supersession-graph-validate:
	$(PY) scripts/validate_corpus_supersession_graph.py

corpus-cross-reference-graph-validate:
	$(PY) scripts/validate_corpus_cross_reference_graph.py

cross-reference-resolution-audit:
	$(PY) scripts/audit_cross_reference_resolution.py

# Reports which tracks say in their own text that they replace something the
# hand-classified supersession graph carries no edge for. Reporting only —
# adding the edge is still a human's job. Run after every ingestion round.
unrecorded-supersessions-audit:
	$(PY) scripts/audit_unrecorded_supersessions.py

# LIVE NETWORK. Not part of the QA gate. Compares the gazette's declared
# sitemaps against the archive index this corpus holds and reports pages it
# has never examined. Run after every ingestion round.
gazette-index-freshness:
	$(PY) scripts/check_gazette_index_freshness.py

corpus-glossary-validate:
	$(PY) scripts/validate_corpus_glossary.py

corpus-schema-manifest-validate:
	$(PY) scripts/validate_corpus_schema_manifest.py

corpus-chunking-layer-validate:
	$(PY) scripts/validate_corpus_chunking_layer.py

corpus-freshness-manifest-validate:
	$(PY) scripts/validate_corpus_freshness_manifest.py

corpus-caveat-layer-validate:
	$(PY) scripts/validate_corpus_caveat_layer.py

patent-law-track-validate:
	$(PY) scripts/validate_patent_law_track.py

customs-law-track-validate:
	$(PY) scripts/validate_customs_law_track.py

customs-regulation-track-validate:
	$(PY) scripts/validate_customs_regulation_track.py

anti-fraud-law-track-validate:
	$(PY) scripts/validate_anti_fraud_law_track.py

finance-companies-law-track-validate:
	$(PY) scripts/validate_finance_companies_law_track.py

cooperative-health-insurance-law-track-validate:
	$(PY) scripts/validate_cooperative_health_insurance_law_track.py

healthcare-professions-law-track-validate:
	$(PY) scripts/validate_healthcare_professions_law_track.py

finance-lease-law-track-validate:
	$(PY) scripts/validate_finance_lease_law_track.py

maritime-commercial-law-track-validate:
	$(PY) scripts/validate_maritime_commercial_law_track.py

gcc-anti-dumping-law-track-validate:
	$(PY) scripts/validate_gcc_anti_dumping_law_track.py

accounting-auditing-law-track-validate:
	$(PY) scripts/validate_accounting_auditing_law_track.py

nazaha-law-track-validate:
	$(PY) scripts/validate_nazaha_law_track.py

awqaf-law-track-validate:
	$(PY) scripts/validate_awqaf_law_track.py

saudi-engineers-law-track-validate:
	$(PY) scripts/validate_saudi_engineers_law_track.py

municipal-councils-law-track-validate:
	$(PY) scripts/validate_municipal_councils_law_track.py

press-law-track-validate:
	$(PY) scripts/validate_press_law_track.py

engineering-practice-law-track-validate:
	$(PY) scripts/validate_engineering_practice_law_track.py

nationality-law-track-validate:
	$(PY) scripts/validate_nationality_law_track.py

residency-law-track-validate:
	$(PY) scripts/validate_residency_law_track.py

civil-status-law-track-validate:
	$(PY) scripts/validate_civil_status_law_track.py

food-law-track-validate:
	$(PY) scripts/validate_food_law_track.py

health-system-law-track-validate:
	$(PY) scripts/validate_health_system_law_track.py

domestic-labor-regulation-track-validate:
	$(PY) scripts/validate_domestic_labor_regulation_track.py

travel-documents-law-track-validate:
	$(PY) scripts/validate_travel_documents_law_track.py

cybersecurity-authority-law-track-validate:
	$(PY) scripts/validate_cybersecurity_authority_law_track.py

cybersecurity-authority-enablers-track-validate:
	$(PY) scripts/validate_cybersecurity_authority_enablers_track.py

premium-residency-law-track-validate:
	$(PY) scripts/validate_premium_residency_law_track.py

travel-documents-regulation-track-validate:
	$(PY) scripts/validate_travel_documents_regulation_track.py

nationality-regulation-track-validate:
	$(PY) scripts/validate_nationality_regulation_track.py

health-system-regulation-track-validate:
	$(PY) scripts/validate_health_system_regulation_track.py

food-regulation-track-validate:
	$(PY) scripts/validate_food_regulation_track.py

electricity-law-track-validate:
	$(PY) scripts/validate_electricity_law_track.py

water-law-track-validate:
	$(PY) scripts/validate_water_law_track.py

vat-regulation-track-validate:
	$(PY) scripts/validate_vat_regulation_track.py

income-tax-regulation-track-validate:
	$(PY) scripts/validate_income_tax_regulation_track.py

agriculture-law-track-validate:
	$(PY) scripts/validate_agriculture_law_track.py

competition-regulation-track-validate:
	$(PY) scripts/validate_competition_regulation_track.py

aml-regulation-track-validate:
	$(PY) scripts/validate_aml_regulation_track.py

patent-regulation-track-validate:
	$(PY) scripts/validate_patent_regulation_track.py

ecommerce-regulation-track-validate:
	$(PY) scripts/validate_ecommerce_regulation_track.py

franchise-regulation-track-validate:
	$(PY) scripts/validate_franchise_regulation_track.py

traffic-regulation-track-validate:
	$(PY) scripts/validate_traffic_regulation_track.py

environmental-inspection-audit-reg-track-validate:
	$(PY) scripts/validate_environmental_inspection_audit_reg_track.py

environmental-violations-penalties-reg-track-validate:
	$(PY) scripts/validate_environmental_violations_penalties_reg_track.py

environmental-wildlife-hunting-reg-track-validate:
	$(PY) scripts/validate_environmental_wildlife_hunting_reg_track.py

environmental-permits-reg-track-validate:
	$(PY) scripts/validate_environmental_permits_reg_track.py

environmental-air-quality-reg-track-validate:
	$(PY) scripts/validate_environmental_air_quality_reg_track.py

environmental-service-providers-reg-track-validate:
	$(PY) scripts/validate_environmental_service_providers_reg_track.py

environmental-fees-reg-track-validate:
	$(PY) scripts/validate_environmental_fees_reg_track.py

rett-law-track-validate:
	$(PY) scripts/validate_rett_law_track.py

universities-law-track-validate:
	$(PY) scripts/validate_universities_law_track.py

privatization-law-track-validate:
	$(PY) scripts/validate_privatization_law_track.py

antiquities-heritage-law-track-validate:
	$(PY) scripts/validate_antiquities_heritage_law_track.py

child-protection-law-track-validate:
	$(PY) scripts/validate_child_protection_law_track.py

protection-from-abuse-law-track-validate:
	$(PY) scripts/validate_protection_from_abuse_law_track.py

associations-ngo-law-track-validate:
	$(PY) scripts/validate_associations_ngo_law_track.py

audiovisual-media-law-track-validate:
	$(PY) scripts/validate_audiovisual_media_law_track.py

sports-law-track-validate:
	$(PY) scripts/validate_sports_law_track.py

anti-smoking-law-track-validate:
	$(PY) scripts/validate_anti_smoking_law_track.py

weapons-ammunition-law-track-validate:
	$(PY) scripts/validate_weapons_ammunition_law_track.py

prison-detention-law-track-validate:
	$(PY) scripts/validate_prison_detention_law_track.py

civil-defense-law-track-validate:
	$(PY) scripts/validate_civil_defense_law_track.py

cooperative-societies-law-track-validate:
	$(PY) scripts/validate_cooperative_societies_law_track.py

building-code-law-track-validate:
	$(PY) scripts/validate_building_code_law_track.py

product-safety-law-track-validate:
	$(PY) scripts/validate_product_safety_law_track.py

standards-quality-law-track-validate:
	$(PY) scripts/validate_standards_quality_law_track.py

disability-rights-law-track-validate:
	$(PY) scripts/validate_disability_rights_law_track.py

tourism-law-track-validate:
	$(PY) scripts/validate_tourism_law_track.py

tourism-travel-services-reg-track-validate:
	$(PY) scripts/validate_tourism_travel_services_reg_track.py

hospitality-mgmt-reg-track-validate:
	$(PY) scripts/validate_hospitality_mgmt_reg_track.py

hospitality-facility-reg-track-validate:
	$(PY) scripts/validate_hospitality_facility_reg_track.py

tourist-visa-reg-track-validate:
	$(PY) scripts/validate_tourist_visa_reg_track.py

environmental-noise-reg-track-validate:
	$(PY) scripts/validate_environmental_noise_reg_track.py

environmental-protected-areas-reg-track-validate:
	$(PY) scripts/validate_environmental_protected_areas_reg_track.py

environmental-emergency-response-reg-track-validate:
	$(PY) scripts/validate_environmental_emergency_response_reg_track.py

product-safety-regulation-track-validate:
	$(PY) scripts/validate_product_safety_regulation_track.py

handicrafts-law-track-validate:
	$(PY) scripts/validate_handicrafts_law_track.py

medical-devices-law-track-validate:
	$(PY) scripts/validate_medical_devices_law_track.py

libraries-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_libraries_authority_licensing_regulation_track.py

theater-performing-arts-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_theater_performing_arts_authority_licensing_regulation_track.py

tourist-guidance-regulation-track-validate:
	$(PY) scripts/validate_tourist_guidance_regulation_track.py

king-saud-university-statute-track-validate:
	$(PY) scripts/validate_king_saud_university_statute_track.py

king-faisal-specialist-hospital-statute-track-validate:
	$(PY) scripts/validate_king_faisal_specialist_hospital_statute_track.py

king-khaled-eye-hospital-statute-track-validate:
	$(PY) scripts/validate_king_khaled_eye_hospital_statute_track.py

state-property-acquisition-controls-track-validate:
	$(PY) scripts/validate_state_property_acquisition_controls_track.py

rehabilitation-and-damage-compensation-rules-track-validate:
	$(PY) scripts/validate_rehabilitation_and_damage_compensation_rules_track.py

export-restriction-governance-statute-track-validate:
	$(PY) scripts/validate_export_restriction_governance_statute_track.py

occupational-fitness-examinations-regulation-track-validate:
	$(PY) scripts/validate_occupational_fitness_examinations_regulation_track.py

municipal-professions-crafts-licensing-regulation-track-validate:
	$(PY) scripts/validate_municipal_professions_crafts_licensing_regulation_track.py

antifouling-systems-regulation-track-validate:
	$(PY) scripts/validate_antifouling_systems_regulation_track.py

cma-auditors-registration-rules-track-validate:
	$(PY) scripts/validate_cma_auditors_registration_rules_track.py

national-risk-council-statute-track-validate:
	$(PY) scripts/validate_national_risk_council_statute_track.py

public-utility-markets-general-rules-track-validate:
	$(PY) scripts/validate_public_utility_markets_general_rules_track.py

literature-publishing-translation-authority-statute-track-validate:
	$(PY) scripts/validate_literature_publishing_translation_authority_statute_track.py

museums-authority-statute-track-validate:
	$(PY) scripts/validate_museums_authority_statute_track.py

heritage-authority-statute-track-validate:
	$(PY) scripts/validate_heritage_authority_statute_track.py

film-authority-statute-track-validate:
	$(PY) scripts/validate_film_authority_statute_track.py

libraries-authority-statute-track-validate:
	$(PY) scripts/validate_libraries_authority_statute_track.py

architecture-design-authority-statute-track-validate:
	$(PY) scripts/validate_architecture_design_authority_statute_track.py

music-authority-statute-track-validate:
	$(PY) scripts/validate_music_authority_statute_track.py

theater-performing-arts-authority-statute-track-validate:
	$(PY) scripts/validate_theater_performing_arts_authority_statute_track.py

visual-arts-authority-statute-track-validate:
	$(PY) scripts/validate_visual_arts_authority_statute_track.py

culinary-arts-authority-statute-track-validate:
	$(PY) scripts/validate_culinary_arts_authority_statute_track.py

fashion-authority-statute-track-validate:
	$(PY) scripts/validate_fashion_authority_statute_track.py

vehicle-periodic-inspection-statute-track-validate:
	$(PY) scripts/validate_vehicle_periodic_inspection_statute_track.py

public-transport-users-rights-regulation-track-validate:
	$(PY) scripts/validate_public_transport_users_rights_regulation_track.py

sez-cloud-computing-regulation-track-validate:
	$(PY) scripts/validate_sez_cloud_computing_regulation_track.py

alula-royal-commission-violations-committees-rules-track-validate:
	$(PY) scripts/validate_alula_royal_commission_violations_committees_rules_track.py

nonprofit-center-supervisory-bodies-relations-regulation-track-validate:
	$(PY) scripts/validate_nonprofit_center_supervisory_bodies_relations_regulation_track.py

saudi-yachts-regulation-track-validate:
	$(PY) scripts/validate_saudi_yachts_regulation_track.py

zakat-tax-accounting-services-rules-track-validate:
	$(PY) scripts/validate_zakat_tax_accounting_services_rules_track.py

national-emergency-management-authority-statute-track-validate:
	$(PY) scripts/validate_national_emergency_management_authority_statute_track.py

riyadh-biotechnology-center-statute-track-validate:
	$(PY) scripts/validate_riyadh_biotechnology_center_statute_track.py

digital-government-authority-statute-track-validate:
	$(PY) scripts/validate_digital_government_authority_statute_track.py

real-estate-development-fund-law-track-validate:
	$(PY) scripts/validate_real_estate_development_fund_law_track.py

building-code-inspection-bodies-regulation-track-validate:
	$(PY) scripts/validate_building_code_inspection_bodies_regulation_track.py

accounting-services-rules-track-validate:
	$(PY) scripts/validate_accounting_services_rules_track.py

king-salman-arabic-language-academy-statute-track-validate:
	$(PY) scripts/validate_king_salman_arabic_language_academy_statute_track.py

biological-weapons-convention-regulation-track-validate:
	$(PY) scripts/validate_biological_weapons_convention_regulation_track.py

national-infrastructure-fund-law-track-validate:
	$(PY) scripts/validate_national_infrastructure_fund_law_track.py

public-auction-sale-rules-track-validate:
	$(PY) scripts/validate_public_auction_sale_rules_track.py

riyadh-nonprofit-foundation-statute-track-validate:
	$(PY) scripts/validate_riyadh_nonprofit_foundation_statute_track.py

state-property-allocation-recovery-controls-track-validate:
	$(PY) scripts/validate_state_property_allocation_recovery_controls_track.py

government-foreign-property-lease-controls-track-validate:
	$(PY) scripts/validate_government_foreign_property_lease_controls_track.py

chemicals-management-regulation-track-validate:
	$(PY) scripts/validate_chemicals_management_regulation_track.py

trustees-experts-fees-rules-track-validate:
	$(PY) scripts/validate_trustees_experts_fees_rules_track.py

metrology-calibration-regulation-track-validate:
	$(PY) scripts/validate_metrology_calibration_regulation_track.py

financial-academy-statute-track-validate:
	$(PY) scripts/validate_financial_academy_statute_track.py

accredited-valuers-fellowship-rules-track-validate:
	$(PY) scripts/validate_accredited_valuers_fellowship_rules_track.py

national-institute-educational-professional-development-statute-track-validate:
	$(PY) scripts/validate_national_institute_educational_professional_development_statute_track.py

hrdf-support-violations-regulation-track-validate:
	$(PY) scripts/validate_hrdf_support_violations_regulation_track.py

agricultural-development-fund-law-track-validate:
	$(PY) scripts/validate_agricultural_development_fund_law_track.py

baha-strategic-office-statute-track-validate:
	$(PY) scripts/validate_baha_strategic_office_statute_track.py

crafts-professions-heads-elections-regulation-track-validate:
	$(PY) scripts/validate_crafts_professions_heads_elections_regulation_track.py

cruise-ships-controls-track-validate:
	$(PY) scripts/validate_cruise_ships_controls_track.py

cultural-development-fund-law-track-validate:
	$(PY) scripts/validate_cultural_development_fund_law_track.py

digital-content-council-statute-track-validate:
	$(PY) scripts/validate_digital_content_council_statute_track.py

energy-allocation-regulation-track-validate:
	$(PY) scripts/validate_energy_allocation_regulation_track.py

enterprise-size-measurement-rules-track-validate:
	$(PY) scripts/validate_enterprise_size_measurement_rules_track.py

final-clearing-collateral-regulation-track-validate:
	$(PY) scripts/validate_final_clearing_collateral_regulation_track.py

food-security-authority-statute-track-validate:
	$(PY) scripts/validate_food_security_authority_statute_track.py

general-irrigation-corporation-statute-track-validate:
	$(PY) scripts/validate_general_irrigation_corporation_statute_track.py

general-roads-authority-statute-track-validate:
	$(PY) scripts/validate_general_roads_authority_statute_track.py

government-property-allocation-transfer-controls-track-validate:
	$(PY) scripts/validate_government_property_allocation_transfer_controls_track.py

government-resource-systems-center-statute-track-validate:
	$(PY) scripts/validate_government_resource_systems_center_statute_track.py

high-industrial-security-authority-statute-track-validate:
	$(PY) scripts/validate_high_industrial_security_authority_statute_track.py

industrial-mining-consultancy-rules-track-validate:
	$(PY) scripts/validate_industrial_mining_consultancy_rules_track.py

jazan-strategic-office-statute-track-validate:
	$(PY) scripts/validate_jazan_strategic_office_statute_track.py

job-seeker-allowance-statute-track-validate:
	$(PY) scripts/validate_job_seeker_allowance_statute_track.py

jouf-strategic-office-statute-track-validate:
	$(PY) scripts/validate_jouf_strategic_office_statute_track.py

kacare-statute-track-validate:
	$(PY) scripts/validate_kacare_statute_track.py

kacst-statute-track-validate:
	$(PY) scripts/validate_kacst_statute_track.py

king-abdullah-language-planning-center-statute-track-validate:
	$(PY) scripts/validate_king_abdullah_language_planning_center_statute_track.py

marina-design-operation-controls-track-validate:
	$(PY) scripts/validate_marina_design_operation_controls_track.py

maritime-travel-ticket-sales-regulation-track-validate:
	$(PY) scripts/validate_maritime_travel_ticket_sales_regulation_track.py

media-regulation-authority-statute-track-validate:
	$(PY) scripts/validate_media_regulation_authority_statute_track.py

municipal-licensing-procedures-regulation-track-validate:
	$(PY) scripts/validate_municipal_licensing_procedures_regulation_track.py

national-curriculum-center-statute-track-validate:
	$(PY) scripts/validate_national_curriculum_center_statute_track.py

national-health-research-institute-statute-track-validate:
	$(PY) scripts/validate_national_health_research_institute_statute_track.py

national-inspection-control-center-statute-track-validate:
	$(PY) scripts/validate_national_inspection_control_center_statute_track.py

national-transport-safety-center-statute-track-validate:
	$(PY) scripts/validate_national_transport_safety_center_statute_track.py

nonprofit-beneficial-owner-rules-track-validate:
	$(PY) scripts/validate_nonprofit_beneficial_owner_rules_track.py

nonprofit-sector-development-center-statute-track-validate:
	$(PY) scripts/validate_nonprofit_sector_development_center_statute_track.py

northern-borders-strategic-office-statute-track-validate:
	$(PY) scripts/validate_northern_borders_strategic_office_statute_track.py

occupational-safety-health-council-statute-track-validate:
	$(PY) scripts/validate_occupational_safety_health_council_statute_track.py

palms-dates-center-statute-track-validate:
	$(PY) scripts/validate_palms_dates_center_statute_track.py

prince-mohammed-bin-salman-park-statute-track-validate:
	$(PY) scripts/validate_prince_mohammed_bin_salman_park_statute_track.py

private-entity-client-data-transfer-regulation-track-validate:
	$(PY) scripts/validate_private_entity_client_data_transfer_regulation_track.py

public-health-authority-statute-track-validate:
	$(PY) scripts/validate_public_health_authority_statute_track.py

public-utility-market-facilities-controls-track-validate:
	$(PY) scripts/validate_public_utility_market_facilities_controls_track.py

rdi-authority-statute-track-validate:
	$(PY) scripts/validate_rdi_authority_statute_track.py

real-estate-transaction-tax-regulation-track-validate:
	$(PY) scripts/validate_real_estate_transaction_tax_regulation_track.py

red-crescent-emblem-law-track-validate:
	$(PY) scripts/validate_red_crescent_emblem_law_track.py

red-sea-coral-turtles-authority-statute-track-validate:
	$(PY) scripts/validate_red_sea_coral_turtles_authority_statute_track.py

regional-headquarters-tax-rules-track-validate:
	$(PY) scripts/validate_regional_headquarters_tax_rules_track.py

royal-institute-traditional-arts-statute-track-validate:
	$(PY) scripts/validate_royal_institute_traditional_arts_statute_track.py

safe-manning-regulation-track-validate:
	$(PY) scripts/validate_safe_manning_regulation_track.py

saudi-auditors-accountants-authority-statute-track-validate:
	$(PY) scripts/validate_saudi_auditors_accountants_authority_statute_track.py

saudi-press-agency-statute-track-validate:
	$(PY) scripts/validate_saudi_press_agency_statute_track.py

saudi-red-sea-authority-statute-track-validate:
	$(PY) scripts/validate_saudi_red_sea_authority_statute_track.py

saudi-space-agency-statute-track-validate:
	$(PY) scripts/validate_saudi_space_agency_statute_track.py

saudi-tourism-authority-statute-track-validate:
	$(PY) scripts/validate_saudi_tourism_authority_statute_track.py

saudi-water-authority-statute-track-validate:
	$(PY) scripts/validate_saudi_water_authority_statute_track.py

ship-safety-management-regulation-track-validate:
	$(PY) scripts/validate_ship_safety_management_regulation_track.py

sme-bank-law-track-validate:
	$(PY) scripts/validate_sme_bank_law_track.py

state-property-authority-statute-track-validate:
	$(PY) scripts/validate_state_property_authority_statute_track.py

two-holy-mosques-authority-statute-track-validate:
	$(PY) scripts/validate_two_holy_mosques_authority_statute_track.py

visiting-yachts-controls-track-validate:
	$(PY) scripts/validate_visiting_yachts_controls_track.py

waqf-investment-portfolios-regulation-track-validate:
	$(PY) scripts/validate_waqf_investment_portfolios_regulation_track.py

white-land-fees-executive-regulation-track-validate:
	$(PY) scripts/validate_white_land_fees_executive_regulation_track.py

wildlife-trade-regulation-track-validate:
	$(PY) scripts/validate_wildlife_trade_regulation_track.py

zatca-statute-track-validate:
	$(PY) scripts/validate_zatca_statute_track.py

arabian-horse-regulation-track-validate:
	$(PY) scripts/validate_arabian_horse_regulation_track.py

classification-societies-authorisation-regulation-track-validate:
	$(PY) scripts/validate_classification_societies_authorisation_regulation_track.py

community-funds-rules-track-validate:
	$(PY) scripts/validate_community_funds_rules_track.py

competencies-contractors-program-rules-track-validate:
	$(PY) scripts/validate_competencies_contractors_program_rules_track.py

conformity-models-general-regulation-track-validate:
	$(PY) scripts/validate_conformity_models_general_regulation_track.py

continuing-professional-education-rules-track-validate:
	$(PY) scripts/validate_continuing_professional_education_rules_track.py

dry-gas-tankers-technical-regulation-track-validate:
	$(PY) scripts/validate_dry_gas_tankers_technical_regulation_track.py

electromagnetic-compatibility-technical-regulation-track-validate:
	$(PY) scripts/validate_electromagnetic_compatibility_technical_regulation_track.py

environmental-rehabilitation-contaminated-sites-regulation-track-validate:
	$(PY) scripts/validate_environmental_rehabilitation_contaminated_sites_regulation_track.py

explosive-atmospheres-equipment-technical-regulation-track-validate:
	$(PY) scripts/validate_explosive_atmospheres_equipment_technical_regulation_track.py

foreign-investment-securities-rules-track-validate:
	$(PY) scripts/validate_foreign_investment_securities_rules_track.py

government-allocation-objections-committee-rules-track-validate:
	$(PY) scripts/validate_government_allocation_objections_committee_rules_track.py

hazardous-substances-electrical-equipment-regulation-track-validate:
	$(PY) scripts/validate_hazardous_substances_electrical_equipment_regulation_track.py

jewellery-accessories-technical-regulation-track-validate:
	$(PY) scripts/validate_jewellery_accessories_technical_regulation_track.py

kacaah-horse-disposal-regulation-track-validate:
	$(PY) scripts/validate_kacaah_horse_disposal_regulation_track.py

king-abdulaziz-reserve-beekeeping-controls-track-validate:
	$(PY) scripts/validate_king_abdulaziz_reserve_beekeeping_controls_track.py

king-abdulaziz-reserve-tourism-permits-controls-track-validate:
	$(PY) scripts/validate_king_abdulaziz_reserve_tourism_permits_controls_track.py

land-customs-storage-fees-controls-track-validate:
	$(PY) scripts/validate_land_customs_storage_fees_controls_track.py

leather-products-technical-regulation-track-validate:
	$(PY) scripts/validate_leather_products_technical_regulation_track.py

makkah-holy-sites-transport-center-regulation-track-validate:
	$(PY) scripts/validate_makkah_holy_sites_transport_center_regulation_track.py

marina-bunkering-controls-track-validate:
	$(PY) scripts/validate_marina_bunkering_controls_track.py

maritime-education-training-accreditation-regulation-track-validate:
	$(PY) scripts/validate_maritime_education_training_accreditation_regulation_track.py

maritime-service-record-regulation-track-validate:
	$(PY) scripts/validate_maritime_service_record_regulation_track.py

maritime-tour-operator-regulation-track-validate:
	$(PY) scripts/validate_maritime_tour_operator_regulation_track.py

maritime-tourism-agent-controls-track-validate:
	$(PY) scripts/validate_maritime_tourism_agent_controls_track.py

maritime-tourism-craft-classification-controls-track-validate:
	$(PY) scripts/validate_maritime_tourism_craft_classification_controls_track.py

medical-referrals-center-statute-track-validate:
	$(PY) scripts/validate_medical_referrals_center_statute_track.py

ozone-depleting-substances-regulation-track-validate:
	$(PY) scripts/validate_ozone_depleting_substances_regulation_track.py

paper-cardboard-technical-regulation-track-validate:
	$(PY) scripts/validate_paper_cardboard_technical_regulation_track.py

public-agencies-staff-provisions-rules-track-validate:
	$(PY) scripts/validate_public_agencies_staff_provisions_rules_track.py

real-estate-consultancy-analytics-regulation-track-validate:
	$(PY) scripts/validate_real_estate_consultancy_analytics_regulation_track.py

real-estate-contributions-escrow-controls-track-validate:
	$(PY) scripts/validate_real_estate_contributions_escrow_controls_track.py

real-estate-market-analysis-controls-track-validate:
	$(PY) scripts/validate_real_estate_market_analysis_controls_track.py

returned-goods-customs-exemption-controls-track-validate:
	$(PY) scripts/validate_returned_goods_customs_exemption_controls_track.py

riyadh-infrastructure-projects-compliance-controls-track-validate:
	$(PY) scripts/validate_riyadh_infrastructure_projects_compliance_controls_track.py

sarah-sudairi-womens-studies-center-statute-track-validate:
	$(PY) scripts/validate_sarah_sudairi_womens_studies_center_statute_track.py

sedimentary-shelf-well-drilling-permits-controls-track-validate:
	$(PY) scripts/validate_sedimentary_shelf_well_drilling_permits_controls_track.py

service-centers-fuel-stations-committee-rules-track-validate:
	$(PY) scripts/validate_service_centers_fuel_stations_committee_rules_track.py

shareek-program-center-statute-track-validate:
	$(PY) scripts/validate_shareek_program_center_statute_track.py

special-use-vehicle-equipment-technical-regulation-track-validate:
	$(PY) scripts/validate_special_use_vehicle_equipment_technical_regulation_track.py

superyacht-chartering-controls-track-validate:
	$(PY) scripts/validate_superyacht_chartering_controls_track.py

tobacco-products-submission-fees-regulation-track-validate:
	$(PY) scripts/validate_tobacco_products_submission_fees_regulation_track.py

tourist-destinations-regulation-track-validate:
	$(PY) scripts/validate_tourist_destinations_regulation_track.py

two-holy-mosques-religious-affairs-presidency-statute-track-validate:
	$(PY) scripts/validate_two_holy_mosques_religious_affairs_presidency_statute_track.py

unesco-national-commission-statute-track-validate:
	$(PY) scripts/validate_unesco_national_commission_statute_track.py

used-imported-vehicles-technical-regulation-track-validate:
	$(PY) scripts/validate_used_imported_vehicles_technical_regulation_track.py

vegetation-cover-desertification-regulation-track-validate:
	$(PY) scripts/validate_vegetation_cover_desertification_regulation_track.py

wheat-seasonal-fodder-cultivation-controls-track-validate:
	$(PY) scripts/validate_wheat_seasonal_fodder_cultivation_controls_track.py

zakat-tax-dispute-settlement-committees-rules-track-validate:
	$(PY) scripts/validate_zakat_tax_dispute_settlement_committees_rules_track.py

accredited-valuers-implementing-regulation-track-validate:
	$(PY) scripts/validate_accredited_valuers_implementing_regulation_track.py

administrative-judicial-council-bylaw-track-validate:
	$(PY) scripts/validate_administrative_judicial_council_bylaw_track.py

antiquities-inspection-violations-regulation-track-validate:
	$(PY) scripts/validate_antiquities_inspection_violations_regulation_track.py

antiquities-museums-fund-regulation-track-validate:
	$(PY) scripts/validate_antiquities_museums_fund_regulation_track.py

bankruptcy-information-documents-regulation-track-validate:
	$(PY) scripts/validate_bankruptcy_information_documents_regulation_track.py

bankruptcy-trustees-experts-rules-track-validate:
	$(PY) scripts/validate_bankruptcy_trustees_experts_rules_track.py

bog-enforcement-service-providers-controls-track-validate:
	$(PY) scripts/validate_bog_enforcement_service_providers_controls_track.py

bog-judicial-inspection-regulation-track-validate:
	$(PY) scripts/validate_bog_judicial_inspection_regulation_track.py

building-code-violations-classification-regulation-track-validate:
	$(PY) scripts/validate_building_code_violations_classification_regulation_track.py

capital-market-conduct-regulation-track-validate:
	$(PY) scripts/validate_capital_market_conduct_regulation_track.py

capital-market-institutions-regulation-track-validate:
	$(PY) scripts/validate_capital_market_institutions_regulation_track.py

capital-market-whistleblowing-regulation-track-validate:
	$(PY) scripts/validate_capital_market_whistleblowing_regulation_track.py

chambers-commerce-committees-regulation-track-validate:
	$(PY) scripts/validate_chambers_commerce_committees_regulation_track.py

coastal-tourism-craft-classification-regulation-track-validate:
	$(PY) scripts/validate_coastal_tourism_craft_classification_regulation_track.py

companies-law-implementing-regulation-track-validate:
	$(PY) scripts/validate_companies_law_implementing_regulation_track.py

contractors-classification-regulation-track-validate:
	$(PY) scripts/validate_contractors_classification_regulation_track.py

copyright-law-2026-track-validate:
	$(PY) scripts/validate_copyright_law_2026_track.py

copyright-law-implementing-regulation-track-validate:
	$(PY) scripts/validate_copyright_law_implementing_regulation_track.py

corporate-governance-regulation-track-validate:
	$(PY) scripts/validate_corporate_governance_regulation_track.py

disability-rights-violations-committee-rules-track-validate:
	$(PY) scripts/validate_disability_rights_violations_committee_rules_track.py

donations-collection-law-track-validate:
	$(PY) scripts/validate_donations_collection_law_track.py

economic-cities-marketing-names-controls-track-validate:
	$(PY) scripts/validate_economic_cities_marketing_names_controls_track.py

electricity-violations-regulation-track-validate:
	$(PY) scripts/validate_electricity_violations_regulation_track.py

excavation-permits-regulation-track-validate:
	$(PY) scripts/validate_excavation_permits_regulation_track.py

extremism-countering-center-statute-track-validate:
	$(PY) scripts/validate_extremism_countering_center_statute_track.py

financial-advisory-profession-rules-track-validate:
	$(PY) scripts/validate_financial_advisory_profession_rules_track.py

foreign-law-firms-licensing-regulation-track-validate:
	$(PY) scripts/validate_foreign_law_firms_licensing_regulation_track.py

foreign-university-branches-regulation-track-validate:
	$(PY) scripts/validate_foreign_university_branches_regulation_track.py

franchise-brokerage-controls-track-validate:
	$(PY) scripts/validate_franchise_brokerage_controls_track.py

gcc-registered-vehicles-stay-controls-track-validate:
	$(PY) scripts/validate_gcc_registered_vehicles_stay_controls_track.py

geographical-indications-protection-law-track-validate:
	$(PY) scripts/validate_geographical_indications_protection_law_track.py

government-foreign-property-lease-controls-2023-track-validate:
	$(PY) scripts/validate_government_foreign_property_lease_controls_2023_track.py

government-health-practitioners-private-work-controls-track-validate:
	$(PY) scripts/validate_government_health_practitioners_private_work_controls_track.py

ict-devices-technical-regulation-track-validate:
	$(PY) scripts/validate_ict_devices_technical_regulation_track.py

investment-accounts-instructions-track-validate:
	$(PY) scripts/validate_investment_accounts_instructions_track.py

judicial-service-conflict-of-interest-rules-track-validate:
	$(PY) scripts/validate_judicial_service_conflict_of_interest_rules_track.py

juvenile-homes-regulation-track-validate:
	$(PY) scripts/validate_juvenile_homes_regulation_track.py

light-goods-road-transport-regulation-track-validate:
	$(PY) scripts/validate_light_goods_road_transport_regulation_track.py

listed-jsc-companies-regulation-track-validate:
	$(PY) scripts/validate_listed_jsc_companies_regulation_track.py

marine-coastal-environment-regulation-track-validate:
	$(PY) scripts/validate_marine_coastal_environment_regulation_track.py

ministry-of-investment-statute-track-validate:
	$(PY) scripts/validate_ministry_of_investment_statute_track.py

national-health-insurance-center-statute-track-validate:
	$(PY) scripts/validate_national_health_insurance_center_statute_track.py

navigation-licence-work-permit-regulation-track-validate:
	$(PY) scripts/validate_navigation_licence_work_permit_regulation_track.py

nazaha-criminal-procedure-powers-regulation-track-validate:
	$(PY) scripts/validate_nazaha_criminal_procedure_powers_regulation_track.py

nonprofit-governance-rules-track-validate:
	$(PY) scripts/validate_nonprofit_governance_rules_track.py

nonprofit-zakat-exemption-rules-track-validate:
	$(PY) scripts/validate_nonprofit_zakat_exemption_rules_track.py

personal-data-transfer-abroad-regulation-track-validate:
	$(PY) scripts/validate_personal_data_transfer_abroad_regulation_track.py

pharmaceutical-herbal-establishments-regulation-track-validate:
	$(PY) scripts/validate_pharmaceutical_herbal_establishments_regulation_track.py

postal-law-regulation-track-validate:
	$(PY) scripts/validate_postal_law_regulation_track.py

premium-residency-center-statute-track-validate:
	$(PY) scripts/validate_premium_residency_center_statute_track.py

private-schools-tuition-controls-track-validate:
	$(PY) scripts/validate_private_schools_tuition_controls_track.py

public-facility-names-rules-track-validate:
	$(PY) scripts/validate_public_facility_names_rules_track.py

reconciliation-committees-regulation-track-validate:
	$(PY) scripts/validate_reconciliation_committees_regulation_track.py

regional-headquarters-procurement-controls-track-validate:
	$(PY) scripts/validate_regional_headquarters_procurement_controls_track.py

regional-tourism-development-councils-statute-track-validate:
	$(PY) scripts/validate_regional_tourism_development_councils_statute_track.py

residential-commercial-gas-network-regulation-track-validate:
	$(PY) scripts/validate_residential_commercial_gas_network_regulation_track.py

riyadh-arts-university-statute-track-validate:
	$(PY) scripts/validate_riyadh_arts_university_statute_track.py

riyadh-sez-center-statute-track-validate:
	$(PY) scripts/validate_riyadh_sez_center_statute_track.py

saudi-culture-memory-center-statute-track-validate:
	$(PY) scripts/validate_saudi_culture_memory_center_statute_track.py

security-cameras-law-regulation-track-validate:
	$(PY) scripts/validate_security_cameras_law_regulation_track.py

sez-companies-register-rules-track-validate:
	$(PY) scripts/validate_sez_companies_register_rules_track.py

sez-companies-rules-track-validate:
	$(PY) scripts/validate_sez_companies_rules_track.py

sez-trade-names-rules-track-validate:
	$(PY) scripts/validate_sez_trade_names_rules_track.py

shariah-governance-capital-market-instructions-track-validate:
	$(PY) scripts/validate_shariah_governance_capital_market_instructions_track.py

simplified-investment-funds-instructions-track-validate:
	$(PY) scripts/validate_simplified_investment_funds_instructions_track.py

social-impact-investment-rules-track-validate:
	$(PY) scripts/validate_social_impact_investment_rules_track.py

temporary-work-visas-regulation-track-validate:
	$(PY) scripts/validate_temporary_work_visas_regulation_track.py

tourism-violations-committee-regulation-track-validate:
	$(PY) scripts/validate_tourism_violations_committee_regulation_track.py

violations-penalties-regulation-track-validate:
	$(PY) scripts/validate_violations_penalties_regulation_track.py

waqf-establishment-donations-regulation-track-validate:
	$(PY) scripts/validate_waqf_establishment_donations_regulation_track.py

waqf-owned-taxpayer-zakat-rules-track-validate:
	$(PY) scripts/validate_waqf_owned_taxpayer_zakat_rules_track.py

water-efficiency-center-statute-track-validate:
	$(PY) scripts/validate_water_efficiency_center_statute_track.py

water-electricity-regulatory-authority-statute-track-validate:
	$(PY) scripts/validate_water_electricity_regulatory_authority_statute_track.py

real-estate-advertising-controls-track-validate:
	$(PY) scripts/validate_real_estate_advertising_controls_track.py

king-abdulaziz-quality-award-statute-track-validate:
	$(PY) scripts/validate_king_abdulaziz_quality_award_statute_track.py

estimated-assessment-zakat-rules-track-validate:
	$(PY) scripts/validate_estimated_assessment_zakat_rules_track.py

anti-concealment-status-correction-regulation-track-validate:
	$(PY) scripts/validate_anti_concealment_status_correction_regulation_track.py

state-realestate-monitoring-encroachment-rules-track-validate:
	$(PY) scripts/validate_state_realestate_monitoring_encroachment_rules_track.py

heavy-equipment-regulation-center-statute-track-validate:
	$(PY) scripts/validate_heavy_equipment_regulation_center_statute_track.py

electricity-tariff-technical-controls-track-validate:
	$(PY) scripts/validate_electricity_tariff_technical_controls_track.py

private-training-executive-rules-track-validate:
	$(PY) scripts/validate_private_training_executive_rules_track.py

trade-agreements-governance-mechanism-track-validate:
	$(PY) scripts/validate_trade_agreements_governance_mechanism_track.py

crime-disclosure-financial-rewards-rules-track-validate:
	$(PY) scripts/validate_crime_disclosure_financial_rewards_rules_track.py

global-tourism-academy-statute-track-validate:
	$(PY) scripts/validate_global_tourism_academy_statute_track.py

development-authorities-support-center-statute-track-validate:
	$(PY) scripts/validate_development_authorities_support_center_statute_track.py

licensed-realestate-developers-rules-track-validate:
	$(PY) scripts/validate_licensed_realestate_developers_rules_track.py

mahd-sports-academy-statute-track-validate:
	$(PY) scripts/validate_mahd_sports_academy_statute_track.py

investment-promotion-authority-statute-track-validate:
	$(PY) scripts/validate_investment_promotion_authority_statute_track.py

uqn-staff-transfer-rules-track-validate:
	$(PY) scripts/validate_uqn_staff_transfer_rules_track.py

alahsa-development-authority-statute-track-validate:
	$(PY) scripts/validate_alahsa_development_authority_statute_track.py

ipo-book-building-allocation-instructions-track-validate:
	$(PY) scripts/validate_ipo_book_building_allocation_instructions_track.py

service-suspension-controls-track-validate:
	$(PY) scripts/validate_service_suspension_controls_track.py

riyadh-infrastructure-projects-center-statute-track-validate:
	$(PY) scripts/validate_riyadh_infrastructure_projects_center_statute_track.py

accounting-services-corrective-mechanism-track-validate:
	$(PY) scripts/validate_accounting_services_corrective_mechanism_track.py

investment-council-statute-track-validate:
	$(PY) scripts/validate_investment_council_statute_track.py

board-committee-remuneration-controls-track-validate:
	$(PY) scripts/validate_board_committee_remuneration_controls_track.py

jeddah-development-authority-statute-track-validate:
	$(PY) scripts/validate_jeddah_development_authority_statute_track.py

esports-authority-statute-track-validate:
	$(PY) scripts/validate_esports_authority_statute_track.py

national-place-names-in-commercial-names-controls-track-validate:
	$(PY) scripts/validate_national_place_names_in_commercial_names_controls_track.py

temporary-camel-auctions-controls-track-validate:
	$(PY) scripts/validate_temporary_camel_auctions_controls_track.py

state-realestate-nonprofit-allocation-controls-track-validate:
	$(PY) scripts/validate_state_realestate_nonprofit_allocation_controls_track.py

corruption-financial-settlements-rules-track-validate:
	$(PY) scripts/validate_corruption_financial_settlements_rules_track.py

government-vehicle-purchase-lease-controls-track-validate:
	$(PY) scripts/validate_government_vehicle_purchase_lease_controls_track.py

official-travel-class-rules-track-validate:
	$(PY) scripts/validate_official_travel_class_rules_track.py

private-healthcare-purchasing-mechanism-track-validate:
	$(PY) scripts/validate_private_healthcare_purchasing_mechanism_track.py

distinguished-competencies-incentive-controls-track-validate:
	$(PY) scripts/validate_distinguished_competencies_incentive_controls_track.py

secondary-data-use-general-rules-track-validate:
	$(PY) scripts/validate_secondary_data_use_general_rules_track.py

arabic-calligraphy-center-statute-track-validate:
	$(PY) scripts/validate_arabic_calligraphy_center_statute_track.py

treaty-brazil-visit-visas-track-validate:
	$(PY) scripts/validate_treaty_brazil_visit_visas_track.py

treaty-aircraft-seizure-supplementary-protocol-track-validate:
	$(PY) scripts/validate_treaty_aircraft_seizure_supplementary_protocol_track.py

treaty-unwto-cooperation-track-validate:
	$(PY) scripts/validate_treaty_unwto_cooperation_track.py

treaty-chad-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_chad_general_cooperation_track.py

treaty-gcc-payment-systems-linkage-track-validate:
	$(PY) scripts/validate_treaty_gcc_payment_systems_linkage_track.py

treaty-regional-technical-cooperation-protocol-track-validate:
	$(PY) scripts/validate_treaty_regional_technical_cooperation_protocol_track.py

treaty-bahrain-customs-cooperation-track-validate:
	$(PY) scripts/validate_treaty_bahrain_customs_cooperation_track.py

treaty-taipei-economic-cultural-office-track-validate:
	$(PY) scripts/validate_treaty_taipei_economic_cultural_office_track.py

treaty-iraq-double-taxation-track-validate:
	$(PY) scripts/validate_treaty_iraq_double_taxation_track.py

treaty-rwanda-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_rwanda_general_cooperation_track.py

treaty-iata-headquarters-track-validate:
	$(PY) scripts/validate_treaty_iata_headquarters_track.py

treaty-ifad-headquarters-track-validate:
	$(PY) scripts/validate_treaty_ifad_headquarters_track.py

state-revenue-law-1448-track-validate:
	$(PY) scripts/validate_state_revenue_law_1448_track.py

motorcycle-freight-transport-regulation-track-validate:
	$(PY) scripts/validate_motorcycle_freight_transport_regulation_track.py

gcc-jointly-owned-property-rules-track-validate:
	$(PY) scripts/validate_gcc_jointly_owned_property_rules_track.py

real-estate-exchange-transfer-mechanism-track-validate:
	$(PY) scripts/validate_real_estate_exchange_transfer_mechanism_track.py

sez-economic-substance-regulation-track-validate:
	$(PY) scripts/validate_sez_economic_substance_regulation_track.py

treaty-gcc-wildlife-conservation-track-validate:
	$(PY) scripts/validate_treaty_gcc_wildlife_conservation_track.py

treaty-unwto-elearning-capacity-track-validate:
	$(PY) scripts/validate_treaty_unwto_elearning_capacity_track.py

treaty-qatar-air-services-track-validate:
	$(PY) scripts/validate_treaty_qatar_air_services_track.py

treaty-pakistan-transfer-of-sentenced-persons-track-validate:
	$(PY) scripts/validate_treaty_pakistan_transfer_of_sentenced_persons_track.py

treaty-unccd-secretariat-cooperation-track-validate:
	$(PY) scripts/validate_treaty_unccd_secretariat_cooperation_track.py

treaty-cameroon-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_cameroon_general_cooperation_track.py

treaty-azerbaijan-customs-assistance-track-validate:
	$(PY) scripts/validate_treaty_azerbaijan_customs_assistance_track.py

treaty-south-sudan-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_south_sudan_general_cooperation_track.py

treaty-greece-maritime-transport-track-validate:
	$(PY) scripts/validate_treaty_greece_maritime_transport_track.py

treaty-hungary-air-services-track-validate:
	$(PY) scripts/validate_treaty_hungary_air_services_track.py

treaty-iraq-maritime-transport-track-validate:
	$(PY) scripts/validate_treaty_iraq_maritime_transport_track.py

treaty-albania-driving-licences-track-validate:
	$(PY) scripts/validate_treaty_albania_driving_licences_track.py

treaty-bangladesh-customs-assistance-track-validate:
	$(PY) scripts/validate_treaty_bangladesh_customs_assistance_track.py

treaty-iala-establishment-track-validate:
	$(PY) scripts/validate_treaty_iala_establishment_track.py

treaty-ghana-air-services-track-validate:
	$(PY) scripts/validate_treaty_ghana_air_services_track.py

treaty-guyana-air-services-track-validate:
	$(PY) scripts/validate_treaty_guyana_air_services_track.py

treaty-djibouti-maritime-transport-track-validate:
	$(PY) scripts/validate_treaty_djibouti_maritime_transport_track.py

treaty-czechia-air-services-track-validate:
	$(PY) scripts/validate_treaty_czechia_air_services_track.py

treaty-dco-headquarters-track-validate:
	$(PY) scripts/validate_treaty_dco_headquarters_track.py

treaty-nepal-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_nepal_general_cooperation_track.py

treaty-arab-road-passenger-transport-track-validate:
	$(PY) scripts/validate_treaty_arab_road_passenger_transport_track.py

treaty-uzbekistan-energy-cooperation-track-validate:
	$(PY) scripts/validate_treaty_uzbekistan_energy_cooperation_track.py

treaty-arab-anti-human-cloning-track-validate:
	$(PY) scripts/validate_treaty_arab_anti_human_cloning_track.py

treaty-latvia-economic-cooperation-track-validate:
	$(PY) scripts/validate_treaty_latvia_economic_cooperation_track.py

treaty-honduras-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_honduras_general_cooperation_track.py

treaty-estonia-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_estonia_general_cooperation_track.py

treaty-cyprus-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_cyprus_general_cooperation_track.py

treaty-slovakia-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_slovakia_general_cooperation_track.py

treaty-slovenia-general-cooperation-track-validate:
	$(PY) scripts/validate_treaty_slovenia_general_cooperation_track.py

occupational-safety-health-national-policy-track-validate:
	$(PY) scripts/validate_occupational_safety_health_national_policy_track.py

spending-efficiency-authority-statute-track-validate:
	$(PY) scripts/validate_spending_efficiency_authority_statute_track.py

realestate-platform-licensing-criteria-track-validate:
	$(PY) scripts/validate_realestate_platform_licensing_criteria_track.py

administrative-violations-drafting-guide-track-validate:
	$(PY) scripts/validate_administrative_violations_drafting_guide_track.py

fresh-produce-import-controls-track-validate:
	$(PY) scripts/validate_fresh_produce_import_controls_track.py

direct-finance-investment-funds-instructions-track-validate:
	$(PY) scripts/validate_direct_finance_investment_funds_instructions_track.py

public-transport-projects-framework-track-validate:
	$(PY) scripts/validate_public_transport_projects_framework_track.py

intracity-bus-transport-licensing-track-validate:
	$(PY) scripts/validate_intracity_bus_transport_licensing_track.py

narcotics-schedules-general-provisions-track-validate:
	$(PY) scripts/validate_narcotics_schedules_general_provisions_track.py

listed-companies-accumulated-losses-instructions-track-validate:
	$(PY) scripts/validate_listed_companies_accumulated_losses_instructions_track.py

charitable-donations-executive-instructions-track-validate:
	$(PY) scripts/validate_charitable_donations_executive_instructions_track.py

railway-independent-consultant-guide-track-validate:
	$(PY) scripts/validate_railway_independent_consultant_guide_track.py

nazaha-military-personnel-statute-track-validate:
	$(PY) scripts/validate_nazaha_military_personnel_statute_track.py

self-consumption-renewable-energy-framework-track-validate:
	$(PY) scripts/validate_self_consumption_renewable_energy_framework_track.py

offplan-engineering-consultants-qualification-track-validate:
	$(PY) scripts/validate_offplan_engineering_consultants_qualification_track.py

civil-aviation-economic-policy-track-validate:
	$(PY) scripts/validate_civil_aviation_economic_policy_track.py

aquaculture-national-policies-guide-track-validate:
	$(PY) scripts/validate_aquaculture_national_policies_guide_track.py

gcc-financial-products-cross-registration-framework-track-validate:
	$(PY) scripts/validate_gcc_financial_products_cross_registration_framework_track.py

animal-health-guide-track-validate:
	$(PY) scripts/validate_animal_health_guide_track.py

abattoirs-meat-inspection-guide-track-validate:
	$(PY) scripts/validate_abattoirs_meat_inspection_guide_track.py

rural-livestock-husbandry-guide-track-validate:
	$(PY) scripts/validate_rural_livestock_husbandry_guide_track.py

vehicle-damage-assessment-standards-track-validate:
	$(PY) scripts/validate_vehicle_damage_assessment_standards_track.py

public-entities-governance-guide-track-validate:
	$(PY) scripts/validate_public_entities_governance_guide_track.py

public-transport-users-rights-enforcement-guide-track-validate:
	$(PY) scripts/validate_public_transport_users_rights_enforcement_guide_track.py

land-transport-training-centers-accreditation-track-validate:
	$(PY) scripts/validate_land_transport_training_centers_accreditation_track.py

arabic-language-national-policy-track-validate:
	$(PY) scripts/validate_arabic_language_national_policy_track.py

gcc-healthcare-waste-management-system-track-validate:
	$(PY) scripts/validate_gcc_healthcare_waste_management_system_track.py

offplan-developer-technical-financial-qualification-track-validate:
	$(PY) scripts/validate_offplan_developer_technical_financial_qualification_track.py

hydrogen-vehicles-technical-regulation-track-validate:
	$(PY) scripts/validate_hydrogen_vehicles_technical_regulation_track.py

cableway-installations-technical-regulation-track-validate:
	$(PY) scripts/validate_cableway_installations_technical_regulation_track.py

bog-enforcement-implementing-regulation-track-validate:
	$(PY) scripts/validate_bog_enforcement_implementing_regulation_track.py

administrative-entities-enforcement-request-procedures-track-validate:
	$(PY) scripts/validate_administrative_entities_enforcement_request_procedures_track.py

cloud-computing-electricity-tariff-executive-rules-track-validate:
	$(PY) scripts/validate_cloud_computing_electricity_tariff_executive_rules_track.py

open-field-vegetable-crops-export-conditions-track-validate:
	$(PY) scripts/validate_open_field_vegetable_crops_export_conditions_track.py

mobile-generation-electricity-service-rules-track-validate:
	$(PY) scripts/validate_mobile_generation_electricity_service_rules_track.py

guaranteed-standards-guide-track-validate:
	$(PY) scripts/validate_guaranteed_standards_guide_track.py

heavy-equipment-safety-inspection-bodies-accreditation-rules-track-validate:
	$(PY) scripts/validate_heavy_equipment_safety_inspection_bodies_accreditation_rules_track.py

emergency-orders-annulment-claims-rules-track-validate:
	$(PY) scripts/validate_emergency_orders_annulment_claims_rules_track.py

hague-apostille-convention-track-validate:
	$(PY) scripts/validate_hague_apostille_convention_track.py

arab-states-transit-transport-agreement-track-validate:
	$(PY) scripts/validate_arab_states_transit_transport_agreement_track.py

copyright-protection-implementing-regulation-track-validate:
	$(PY) scripts/validate_copyright_protection_implementing_regulation_track.py

real-estate-development-fund-implementing-regulation-track-validate:
	$(PY) scripts/validate_real_estate_development_fund_implementing_regulation_track.py

experimental-activities-regulation-track-validate:
	$(PY) scripts/validate_experimental_activities_regulation_track.py

visiting-private-yachts-regulation-track-validate:
	$(PY) scripts/validate_visiting_private_yachts_regulation_track.py

cruise-ships-regulation-track-validate:
	$(PY) scripts/validate_cruise_ships_regulation_track.py

securities-offering-rules-track-validate:
	$(PY) scripts/validate_securities_offering_rules_track.py

superyacht-chartering-regulation-track-validate:
	$(PY) scripts/validate_superyacht_chartering_regulation_track.py

utility-benefit-loss-compensation-regulation-track-validate:
	$(PY) scripts/validate_utility_benefit_loss_compensation_regulation_track.py

repair-cost-compensation-estimation-controls-track-validate:
	$(PY) scripts/validate_repair_cost_compensation_estimation_controls_track.py

museums-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_museums_authority_licensing_regulation_track.py

heritage-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_heritage_authority_licensing_regulation_track.py

literature-publishing-translation-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_literature_publishing_translation_authority_licensing_regulation_track.py

film-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_film_authority_licensing_regulation_track.py

fashion-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_fashion_authority_licensing_regulation_track.py

music-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_music_authority_licensing_regulation_track.py

culinary-arts-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_culinary_arts_authority_licensing_regulation_track.py

architecture-design-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_architecture_design_authority_licensing_regulation_track.py

visual-arts-authority-licensing-regulation-track-validate:
	$(PY) scripts/validate_visual_arts_authority_licensing_regulation_track.py

tourism-consultancy-regulation-track-validate:
	$(PY) scripts/validate_tourism_consultancy_regulation_track.py

tourism-activity-inspection-regulation-track-validate:
	$(PY) scripts/validate_tourism_activity_inspection_regulation_track.py

duty-free-markets-rules-track-validate:
	$(PY) scripts/validate_duty_free_markets_rules_track.py

driving-schools-regulation-track-validate:
	$(PY) scripts/validate_driving_schools_regulation_track.py

railway-violations-committee-rules-track-validate:
	$(PY) scripts/validate_railway_violations_committee_rules_track.py

public-transport-users-rights-mechanism-track-validate:
	$(PY) scripts/validate_public_transport_users_rights_mechanism_track.py

gcc-pesticides-regulation-track-validate:
	$(PY) scripts/validate_gcc_pesticides_regulation_track.py

military-industries-rnd-regulation-track-validate:
	$(PY) scripts/validate_military_industries_rnd_regulation_track.py

international-bus-transport-regulation-track-validate:
	$(PY) scripts/validate_international_bus_transport_regulation_track.py

vehicle-periodic-inspection-regulation-track-validate:
	$(PY) scripts/validate_vehicle_periodic_inspection_regulation_track.py

health-specialties-membership-regulation-track-validate:
	$(PY) scripts/validate_health_specialties_membership_regulation_track.py

disability-social-programs-regulation-track-validate:
	$(PY) scripts/validate_disability_social_programs_regulation_track.py

vehicle-damage-assessment-rules-track-validate:
	$(PY) scripts/validate_vehicle_damage_assessment_rules_track.py

tourist-accommodation-facilities-regulation-track-validate:
	$(PY) scripts/validate_tourist_accommodation_facilities_regulation_track.py

ngo-council-regulation-track-validate:
	$(PY) scripts/validate_ngo_council_regulation_track.py

health-holding-company-statute-track-validate:
	$(PY) scripts/validate_health_holding_company_statute_track.py

family-funds-rules-track-validate:
	$(PY) scripts/validate_family_funds_rules_track.py

airports-economic-regulation-track-validate:
	$(PY) scripts/validate_airports_economic_regulation_track.py

valuation-profession-conduct-rules-track-validate:
	$(PY) scripts/validate_valuation_profession_conduct_rules_track.py

nazara-works-regulation-track-validate:
	$(PY) scripts/validate_nazara_works_regulation_track.py

ballast-water-regulation-track-validate:
	$(PY) scripts/validate_ballast_water_regulation_track.py

sez-kaec-regulation-track-validate:
	$(PY) scripts/validate_sez_kaec_regulation_track.py

sez-jazan-regulation-track-validate:
	$(PY) scripts/validate_sez_jazan_regulation_track.py

sez-raskhair-regulation-track-validate:
	$(PY) scripts/validate_sez_raskhair_regulation_track.py

charitable-societies-council-regulation-track-validate:
	$(PY) scripts/validate_charitable_societies_council_regulation_track.py

customs-procedures-controls-track-validate:
	$(PY) scripts/validate_customs_procedures_controls_track.py

social-security-regulation-track-validate:
	$(PY) scripts/validate_social_security_regulation_track.py

revenue-sharing-rules-track-validate:
	$(PY) scripts/validate_revenue_sharing_rules_track.py

freight-broker-logistics-regulation-track-validate:
	$(PY) scripts/validate_freight_broker_logistics_regulation_track.py

property-ownership-committees-rules-track-validate:
	$(PY) scripts/validate_property_ownership_committees_rules_track.py

disability-nongov-social-facilities-regulation-track-validate:
	$(PY) scripts/validate_disability_nongov_social_facilities_regulation_track.py

free-zone-employees-treatment-rules-track-validate:
	$(PY) scripts/validate_free_zone_employees_treatment_rules_track.py

inspection-control-seizure-rules-track-validate:
	$(PY) scripts/validate_inspection_control_seizure_rules_track.py

ip-services-licensing-rules-track-validate:
	$(PY) scripts/validate_ip_services_licensing_rules_track.py

deposit-zones-rules-track-validate:
	$(PY) scripts/validate_deposit_zones_rules_track.py

air-transport-services-economic-regulation-track-validate:
	$(PY) scripts/validate_air_transport_services_economic_regulation_track.py

privatization-governing-rules-track-validate:
	$(PY) scripts/validate_privatization_governing_rules_track.py

ground-handling-air-cargo-economic-regulation-track-validate:
	$(PY) scripts/validate_ground_handling_air_cargo_economic_regulation_track.py

museums-regulation-track-validate:
	$(PY) scripts/validate_museums_regulation_track.py

private-universities-regulation-track-validate:
	$(PY) scripts/validate_private_universities_regulation_track.py

gcc-road-transport-law-track-validate:
	$(PY) scripts/validate_gcc_road_transport_law_track.py

marpol-regulation-track-validate:
	$(PY) scripts/validate_marpol_regulation_track.py

securities-disputes-rules-track-validate:
	$(PY) scripts/validate_securities_disputes_rules_track.py

state-realestate-disposal-regulation-track-validate:
	$(PY) scripts/validate_state_realestate_disposal_regulation_track.py

securities-depository-markets-regulation-track-validate:
	$(PY) scripts/validate_securities_depository_markets_regulation_track.py

capital-adequacy-rules-track-validate:
	$(PY) scripts/validate_capital_adequacy_rules_track.py

mergers-acquisitions-regulation-track-validate:
	$(PY) scripts/validate_mergers_acquisitions_regulation_track.py

taxi-activity-regulation-track-validate:
	$(PY) scripts/validate_taxi_activity_regulation_track.py

zakat-tax-customs-committees-rules-track-validate:
	$(PY) scripts/validate_zakat_tax_customs_committees_rules_track.py

official-communications-records-regulation-track-validate:
	$(PY) scripts/validate_official_communications_records_regulation_track.py

housing-support-regulation-track-validate:
	$(PY) scripts/validate_housing_support_regulation_track.py

special-purpose-entities-rules-track-validate:
	$(PY) scripts/validate_special_purpose_entities_rules_track.py

medical-devices-regulation-track-validate:
	$(PY) scripts/validate_medical_devices_regulation_track.py

financial-institutions-resolution-law-track-validate:
	$(PY) scripts/validate_financial_institutions_resolution_law_track.py

trade-remedies-law-track-validate:
	$(PY) scripts/validate_trade_remedies_law_track.py

trade-remedies-regulation-track-validate:
	$(PY) scripts/validate_trade_remedies_regulation_track.py

financial-fraud-law-track-validate:
	$(PY) scripts/validate_financial_fraud_law_track.py

state-property-lease-law-track-validate:
	$(PY) scripts/validate_state_property_lease_law_track.py

state-property-lease-regulation-track-validate:
	$(PY) scripts/validate_state_property_lease_regulation_track.py

job-discipline-law-track-validate:
	$(PY) scripts/validate_job_discipline_law_track.py

statistics-law-track-validate:
	$(PY) scripts/validate_statistics_law_track.py

anti-begging-law-track-validate:
	$(PY) scripts/validate_anti_begging_law_track.py

security-cameras-law-track-validate:
	$(PY) scripts/validate_security_cameras_law_track.py

antiquities-heritage-regulation-track-validate:
	$(PY) scripts/validate_antiquities_heritage_regulation_track.py

meteorology-law-track-validate:
	$(PY) scripts/validate_meteorology_law_track.py

handicrafts-regulation-track-validate:
	$(PY) scripts/validate_handicrafts_regulation_track.py

donations-collection-regulation-track-validate:
	$(PY) scripts/validate_donations_collection_regulation_track.py

falcon-center-statute-track-validate:
	$(PY) scripts/validate_falcon_center_statute_track.py

geographical-indications-regulation-track-validate:
	$(PY) scripts/validate_geographical_indications_regulation_track.py

vacant-properties-fees-regulation-track-validate:
	$(PY) scripts/validate_vacant_properties_fees_regulation_track.py

waqf-investment-products-regulation-track-validate:
	$(PY) scripts/validate_waqf_investment_products_regulation_track.py

insurance-disputes-committees-rules-track-validate:
	$(PY) scripts/validate_insurance_disputes_committees_rules_track.py

entertainment-activities-law-track-validate:
	$(PY) scripts/validate_entertainment_activities_law_track.py

standards-quality-regulation-track-validate:
	$(PY) scripts/validate_standards_quality_regulation_track.py

disability-rights-regulation-track-validate:
	$(PY) scripts/validate_disability_rights_regulation_track.py

anti-smoking-regulation-track-validate:
	$(PY) scripts/validate_anti_smoking_regulation_track.py

general-education-law-track-validate:
	$(PY) scripts/validate_general_education_law_track.py

credit-information-law-track-validate:
	$(PY) scripts/validate_credit_information_law_track.py

real-estate-brokerage-law-track-validate:
	$(PY) scripts/validate_real_estate_brokerage_law_track.py

state-revenue-law-track-validate:
	$(PY) scripts/validate_state_revenue_law_track.py

etec-law-track-validate:
	$(PY) scripts/validate_etec_law_track.py

einvoicing-regulation-track-validate:
	$(PY) scripts/validate_einvoicing_regulation_track.py

pdpl-cross-border-transfer-regulation-track-validate:
	$(PY) scripts/validate_pdpl_cross_border_transfer_regulation_track.py

sdaia-organizational-arrangements-track-validate:
	$(PY) scripts/validate_sdaia_organizational_arrangements_track.py

trade-names-regulation-track-validate:
	$(PY) scripts/validate_trade_names_regulation_track.py

commercial-agencies-regulation-track-validate:
	$(PY) scripts/validate_commercial_agencies_regulation_track.py

accounting-auditing-regulation-track-validate:
	$(PY) scripts/validate_accounting_auditing_regulation_track.py

commercial-register-regulation-track-validate:
	$(PY) scripts/validate_commercial_register_regulation_track.py

real-estate-brokerage-regulation-track-validate:
	$(PY) scripts/validate_real_estate_brokerage_regulation_track.py

foreign-ownership-regulation-track-validate:
	$(PY) scripts/validate_foreign_ownership_regulation_track.py

anti-fraud-regulation-track-validate:
	$(PY) scripts/validate_anti_fraud_regulation_track.py

rett-regulation-track-validate:
	$(PY) scripts/validate_rett_regulation_track.py

anti-narcotics-regulation-track-validate:
	$(PY) scripts/validate_anti_narcotics_regulation_track.py

anti-concealment-regulation-track-validate:
	$(PY) scripts/validate_anti_concealment_regulation_track.py

privatization-regulation-track-validate:
	$(PY) scripts/validate_privatization_regulation_track.py

chambers-of-commerce-regulation-track-validate:
	$(PY) scripts/validate_chambers_of_commerce_regulation_track.py

state-revenue-regulation-track-validate:
	$(PY) scripts/validate_state_revenue_regulation_track.py

weapons-ammunition-regulation-track-validate:
	$(PY) scripts/validate_weapons_ammunition_regulation_track.py

engineering-practice-regulation-track-validate:
	$(PY) scripts/validate_engineering_practice_regulation_track.py

allegiance-commission-regulation-track-validate:
	$(PY) scripts/validate_allegiance_commission_regulation_track.py

social-insurance-regulation-track-validate:
	$(PY) scripts/validate_social_insurance_regulation_track.py

saudi-engineers-regulation-track-validate:
	$(PY) scripts/validate_saudi_engineers_regulation_track.py

child-protection-regulation-track-validate:
	$(PY) scripts/validate_child_protection_regulation_track.py

whistleblower-regulation-track-validate:
	$(PY) scripts/validate_whistleblower_regulation_track.py

social-insurance-legacy-regulation-track-validate:
	$(PY) scripts/validate_social_insurance_legacy_regulation_track.py

protection-from-abuse-regulation-track-validate:
	$(PY) scripts/validate_protection_from_abuse_regulation_track.py

healthcare-professions-regulation-track-validate:
	$(PY) scripts/validate_healthcare_professions_regulation_track.py

shura-council-internal-regulation-track-validate:
	$(PY) scripts/validate_shura_council_internal_regulation_track.py

civil-service-regulation-track-validate:
	$(PY) scripts/validate_civil_service_regulation_track.py

associations-ngo-regulation-track-validate:
	$(PY) scripts/validate_associations_ngo_regulation_track.py

electronic-transactions-regulation-track-validate:
	$(PY) scripts/validate_electronic_transactions_regulation_track.py

electricity-regulation-track-validate:
	$(PY) scripts/validate_electricity_regulation_track.py

maritime-commercial-regulation-track-validate:
	$(PY) scripts/validate_maritime_commercial_regulation_track.py

agriculture-regulation-track-validate:
	$(PY) scripts/validate_agriculture_regulation_track.py

civil-defense-regulation-track-validate:
	$(PY) scripts/validate_civil_defense_regulation_track.py

premium-residency-regulation-track-validate:
	$(PY) scripts/validate_premium_residency_regulation_track.py

water-regulation-track-validate:
	$(PY) scripts/validate_water_regulation_track.py

press-regulation-track-validate:
	$(PY) scripts/validate_press_regulation_track.py

building-code-regulation-track-validate:
	$(PY) scripts/validate_building_code_regulation_track.py

telecommunications-regulation-track-validate:
	$(PY) scripts/validate_telecommunications_regulation_track.py

credit-information-regulation-track-validate:
	$(PY) scripts/validate_credit_information_regulation_track.py

payment-systems-regulation-track-validate:
	$(PY) scripts/validate_payment_systems_regulation_track.py

banking-control-regulation-track-validate:
	$(PY) scripts/validate_banking_control_regulation_track.py

finance-companies-regulation-track-validate:
	$(PY) scripts/validate_finance_companies_regulation_track.py

finance-lease-regulation-track-validate:
	$(PY) scripts/validate_finance_lease_regulation_track.py

cooperative-societies-regulation-track-validate:
	$(PY) scripts/validate_cooperative_societies_regulation_track.py

bog-enforcement-law-track-validate:
	$(PY) scripts/validate_bog_enforcement_law_track.py

public-prosecution-law-track-validate:
	$(PY) scripts/validate_public_prosecution_law_track.py

elderly-care-law-track-validate:
	$(PY) scripts/validate_elderly_care_law_track.py

elderly-care-regulation-track-validate:
	$(PY) scripts/validate_elderly_care_regulation_track.py

private-schools-regulation-track-validate:
	$(PY) scripts/validate_private_schools_regulation_track.py

foreign-schools-regulation-track-validate:
	$(PY) scripts/validate_foreign_schools_regulation_track.py

postal-law-track-validate:
	$(PY) scripts/validate_postal_law_track.py

cma-corporate-governance-regulation-track-validate:
	$(PY) scripts/validate_cma_corporate_governance_regulation_track.py

tvtc-organizational-statute-track-validate:
	$(PY) scripts/validate_tvtc_organizational_statute_track.py

waste-management-law-track-validate:
	$(PY) scripts/validate_waste_management_law_track.py

fisheries-law-track-validate:
	$(PY) scripts/validate_fisheries_law_track.py

debt-collection-regulation-track-validate:
	$(PY) scripts/validate_debt_collection_regulation_track.py

insurance-authority-statute-track-validate:
	$(PY) scripts/validate_insurance_authority_statute_track.py

bnpl-regulation-track-validate:
	$(PY) scripts/validate_bnpl_regulation_track.py

offplan-sale-law-track-validate:
	$(PY) scripts/validate_offplan_sale_law_track.py

contractors-classification-law-track-validate:
	$(PY) scripts/validate_contractors_classification_law_track.py

real-estate-contributions-law-track-validate:
	$(PY) scripts/validate_real_estate_contributions_law_track.py

accredited-valuers-law-track-validate:
	$(PY) scripts/validate_accredited_valuers_law_track.py

white-land-fees-law-track-validate:
	$(PY) scripts/validate_white_land_fees_law_track.py

frequency-spectrum-regulation-track-validate:
	$(PY) scripts/validate_frequency_spectrum_regulation_track.py

mental-health-law-track-validate:
	$(PY) scripts/validate_mental_health_law_track.py

organ-donation-law-track-validate:
	$(PY) scripts/validate_organ_donation_law_track.py

private-healthcare-institutions-law-track-validate:
	$(PY) scripts/validate_private_healthcare_institutions_law_track.py

high-risk-professions-regulation-track-validate:
	$(PY) scripts/validate_high_risk_professions_regulation_track.py

osh-service-providers-regulation-track-validate:
	$(PY) scripts/validate_osh_service_providers_regulation_track.py

rega-organizational-statute-track-validate:
	$(PY) scripts/validate_rega_organizational_statute_track.py

offplan-sale-implementing-regulation-track-validate:
	$(PY) scripts/validate_offplan_sale_implementing_regulation_track.py

real-estate-finance-implementing-regulation-track-validate:
	$(PY) scripts/validate_real_estate_finance_implementing_regulation_track.py

real-estate-contributions-implementing-regulation-track-validate:
	$(PY) scripts/validate_real_estate_contributions_implementing_regulation_track.py

landlord-tenant-relationship-regulation-track-validate:
	$(PY) scripts/validate_landlord_tenant_relationship_regulation_track.py

real-estate-marketing-advertising-regulation-track-validate:
	$(PY) scripts/validate_real_estate_marketing_advertising_regulation_track.py

real-estate-auctions-regulation-track-validate:
	$(PY) scripts/validate_real_estate_auctions_regulation_track.py

petroleum-petrochemical-materials-law-track-validate:
	$(PY) scripts/validate_petroleum_petrochemical_materials_law_track.py

dry-gas-lpg-distribution-law-track-validate:
	$(PY) scripts/validate_dry_gas_lpg_distribution_law_track.py

energy-supplies-system-track-validate:
	$(PY) scripts/validate_energy_supplies_system_track.py

mining-investment-implementing-regulation-track-validate:
	$(PY) scripts/validate_mining_investment_implementing_regulation_track.py

pharmaceutical-establishments-law-track-validate:
	$(PY) scripts/validate_pharmaceutical_establishments_law_track.py

seized-confiscated-funds-management-system-track-validate:
	$(PY) scripts/validate_seized_confiscated_funds_management_system_track.py

nca-cybersecurity-violations-investigation-rules-track-validate:
	$(PY) scripts/validate_nca_cybersecurity_violations_investigation_rules_track.py

nca-cybersecurity-violations-reporting-rules-track-validate:
	$(PY) scripts/validate_nca_cybersecurity_violations_reporting_rules_track.py

cst-organizational-statute-track-validate:
	$(PY) scripts/validate_cst_organizational_statute_track.py

railway-law-track-validate:
	$(PY) scripts/validate_railway_law_track.py

railway-law-implementing-regulation-track-validate:
	$(PY) scripts/validate_railway_law_implementing_regulation_track.py

road-transport-law-track-validate:
	$(PY) scripts/validate_road_transport_law_track.py

gaca-organizational-statute-track-validate:
	$(PY) scripts/validate_gaca_organizational_statute_track.py

tga-organizational-statute-track-validate:
	$(PY) scripts/validate_tga_organizational_statute_track.py

mawani-organizational-statute-track-validate:
	$(PY) scripts/validate_mawani_organizational_statute_track.py

hajj-umrah-external-pilgrims-law-track-validate:
	$(PY) scripts/validate_hajj_umrah_external_pilgrims_law_track.py

aviation-passenger-rights-regulation-track-validate:
	$(PY) scripts/validate_aviation_passenger_rights_regulation_track.py

# -- STRICT QA GATE: every validate_*.py + generator idempotence + full pytest. One command, everything must pass. --
qa-gate:
	$(PY) scripts/run_qa_gate.py

# CI variant (pytest already runs as its own CI step)
qa-gate-ci:
	$(PY) scripts/run_qa_gate.py --no-tests

clean:
	rm -f dist/book1.html dist/book1.pdf data/articles/book1_articles_001_034.jsonl \
	      dist/book2.html dist/book2.pdf data/articles/book2_articles_035_050.jsonl \
	      dist/book3.html dist/book3.pdf data/articles/book3_articles_051_057.jsonl
