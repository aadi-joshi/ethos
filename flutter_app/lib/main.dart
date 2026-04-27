import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

void main() {
  runApp(const EthosApp());
}

const String kApiBase = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

const Color kPrimary = Color(0xFF0F2243);
const Color kAccent = Color(0xFFE63946);
const Color kSuccess = Color(0xFF16A34A);
const Color kWarning = Color(0xFFF59E0B);
const Color kBg = Color(0xFFF1F5F9);

class EthosApp extends StatelessWidget {
  const EthosApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ethos AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: kPrimary,
          primary: kPrimary,
          secondary: kAccent,
          surface: Colors.white,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: kPrimary,
          foregroundColor: Colors.white,
          elevation: 0,
          titleTextStyle: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.w800,
            letterSpacing: -0.5,
          ),
        ),
      ),
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  final List<Widget> _pages = const [HomePage(), ReportPage(), MapPage()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        backgroundColor: Colors.white,
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.report_outlined), selectedIcon: Icon(Icons.report), label: 'Report'),
          NavigationDestination(icon: Icon(Icons.map_outlined), selectedIcon: Icon(Icons.map), label: 'Bias Map'),
        ],
      ),
    );
  }
}

// ── Home Page ─────────────────────────────────────────────────────────────────
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBg,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            backgroundColor: kPrimary,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('Ethos AI',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 20, letterSpacing: -0.5)),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF070F1E), kPrimary, Color(0xFF1A2F54)],
                  ),
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox(height: 32),
                      Text('⊗', style: TextStyle(fontSize: 48, color: kAccent)),
                      SizedBox(height: 4),
                      Text("India's AI Bias Auditor",
                          style: TextStyle(color: Colors.white38, fontSize: 12, letterSpacing: 1)),
                    ],
                  ),
                ),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _introCard(),
                const SizedBox(height: 16),
                _statGrid(),
                const SizedBox(height: 16),
                _featureList(),
                const SizedBox(height: 16),
                _complianceCard(),
                const SizedBox(height: 24),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _introCard() => Container(
    padding: const EdgeInsets.all(20),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFE2E8F0))),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Wrap(spacing: 8, children: const [
        _Tag(label: 'BETA', color: kAccent),
        _Tag(label: 'GOOGLE SOLUTION CHALLENGE 2026', color: Color(0xFF2563EB)),
      ]),
      const SizedBox(height: 14),
      const Text("Bias doesn't hide.\nWe expose it.",
          style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: kPrimary, letterSpacing: -1, height: 1.15)),
      const SizedBox(height: 10),
      const Text(
        "India's first accessible LLM bias auditing platform. Report AI discrimination anonymously. Your data drives policy change.",
        style: TextStyle(fontSize: 14, color: Color(0xFF475569), height: 1.6),
      ),
    ]),
  );

  Widget _statGrid() {
    const stats = [
      ('73%', 'hiring tools show caste bias'),
      ('4', 'protected dimensions'),
      ('6', 'fairness metrics'),
      ('1st', 'India-specific platform'),
    ];
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 2.0, crossAxisSpacing: 10, mainAxisSpacing: 10),
      itemCount: 4,
      itemBuilder: (ctx, i) => Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFE2E8F0))),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(stats[i].$1, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: kPrimary, letterSpacing: -1)),
          Text(stats[i].$2, style: const TextStyle(fontSize: 11, color: Color(0xFF475569))),
        ]),
      ),
    );
  }

  Widget _featureList() {
    const features = [
      ('◎', 'LLM Bias Probe', 'Counterfactual probing: identical prompts, different names. Measurable discrimination.', kAccent),
      ('▦', 'ML Model Audit', 'Upload dataset. Get 6 fairness metrics and reweighed dataset.', Color(0xFF2563EB)),
      ('◉', 'Citizen Bias Map', 'Report AI discrimination anonymously. View India heatmap.', kSuccess),
    ];
    return Column(
      children: features.map((f) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFE2E8F0))),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(f.$1, style: TextStyle(fontSize: 26, color: f.$4)),
            const SizedBox(width: 14),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(f.$2, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: kPrimary)),
              const SizedBox(height: 4),
              Text(f.$3, style: const TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.5)),
            ])),
          ]),
        ),
      )).toList(),
    );
  }

  Widget _complianceCard() => Container(
    padding: const EdgeInsets.all(18),
    decoration: BoxDecoration(color: kPrimary, borderRadius: BorderRadius.circular(14)),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('India Compliance Framework', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w800)),
      const SizedBox(height: 12),
      ...<String>['DPDP Act 2023', 'Articles 15 & 16 (Constitution)', 'RBI Fair Practices Code', 'EEOC Four-Fifths Rule'].map((law) =>
        Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Row(children: [
            const Icon(Icons.check_circle, color: kSuccess, size: 14),
            const SizedBox(width: 8),
            Text(law, style: const TextStyle(color: Colors.white70, fontSize: 13)),
          ]),
        ),
      ),
    ]),
  );
}

class _Tag extends StatelessWidget {
  final String label;
  final Color color;
  const _Tag({required this.label, required this.color});

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(4), border: Border.all(color: color.withValues(alpha: 0.3))),
    child: Text(label, style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.w800, letterSpacing: .8)),
  );
}

// ── Report Page ───────────────────────────────────────────────────────────────
class ReportPage extends StatefulWidget {
  const ReportPage({super.key});

  @override
  State<ReportPage> createState() => _ReportPageState();
}

class _ReportPageState extends State<ReportPage> {
  String _domain = 'hiring';
  String _biasType = 'caste';
  final _descCtrl = TextEditingController();
  String _state = '';
  String _orgType = '';
  bool _consent = true;
  bool _loading = false;
  Map<String, dynamic>? _result;
  String _error = '';

  static const _domains = ['hiring', 'lending', 'education', 'healthcare'];
  static const _biasTypes = ['caste', 'religion', 'gender', 'region'];
  static const _states = ['Andhra Pradesh', 'Assam', 'Bihar', 'Delhi', 'Gujarat', 'Haryana', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'West Bengal', 'Other'];
  static const _orgTypes = ['Private company', 'Government', 'Bank/NBFC', 'Educational institution', 'Healthcare', 'Other'];
  static const _biasColors = {
    'caste': kAccent,
    'religion': Color(0xFF7C3AED),
    'gender': Color(0xFF0891B2),
    'region': kWarning,
  };

  Future<void> _submit() async {
    if (_descCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Please describe the bias you experienced.');
      return;
    }
    setState(() { _loading = true; _error = ''; });
    try {
      final res = await http.post(
        Uri.parse('$kApiBase/citizen/report'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'domain': _domain,
          'bias_type': _biasType,
          'description': _descCtrl.text,
          'state': _state.isEmpty ? null : _state,
          'organization_type': _orgType.isEmpty ? null : _orgType,
          'consent_to_aggregate': _consent,
        }),
      );
      if (res.statusCode == 200) {
        setState(() => _result = jsonDecode(res.body) as Map<String, dynamic>);
      } else {
        final err = jsonDecode(res.body) as Map<String, dynamic>;
        setState(() => _error = (err['detail'] as String?) ?? 'Submission failed');
      }
    } catch (e) {
      setState(() => _error = 'Network error. Ensure the backend is running.');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void dispose() { _descCtrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    if (_result != null) {
      return _SuccessView(result: _result!, onReset: () => setState(() { _result = null; _descCtrl.clear(); }));
    }
    return Scaffold(
      backgroundColor: kBg,
      appBar: AppBar(
        title: const Text('Report AI Bias'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(32),
          child: Container(padding: const EdgeInsets.only(left: 16, bottom: 8), alignment: Alignment.centerLeft,
            child: const Text('ANONYMOUS - AGGREGATED DATA ONLY', style: TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 1))),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _privacyCard(),
          const SizedBox(height: 16),
          _lbl('Domain'),
          _chips(_domains, _domain, (v) => setState(() => _domain = v)),
          const SizedBox(height: 16),
          _lbl('Type of Bias'),
          _biasChips(),
          const SizedBox(height: 16),
          _lbl('What happened? *'),
          TextField(
            controller: _descCtrl, maxLines: 5,
            decoration: InputDecoration(
              hintText: 'What AI system was involved? What decision did it make?',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true, fillColor: Colors.white,
            ),
          ),
          const SizedBox(height: 14),
          Row(children: [
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _lbl('State'),
              DropdownButtonFormField<String>(
                value: _state.isEmpty ? null : _state,
                decoration: InputDecoration(hintText: 'Select', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)), filled: true, fillColor: Colors.white),
                items: _states.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontSize: 13)))).toList(),
                onChanged: (v) => setState(() => _state = v ?? ''),
              ),
            ])),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _lbl('Org type'),
              DropdownButtonFormField<String>(
                value: _orgType.isEmpty ? null : _orgType,
                decoration: InputDecoration(hintText: 'Select', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)), filled: true, fillColor: Colors.white),
                items: _orgTypes.map((o) => DropdownMenuItem(value: o, child: Text(o, style: const TextStyle(fontSize: 13)))).toList(),
                onChanged: (v) => setState(() => _orgType = v ?? ''),
              ),
            ])),
          ]),
          const SizedBox(height: 12),
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Checkbox(value: _consent, onChanged: (v) => setState(() => _consent = v ?? true), activeColor: kPrimary),
            const SizedBox(width: 6),
            const Expanded(child: Text(
              'I consent to this report being aggregated anonymously for research and policy advocacy.',
              style: TextStyle(fontSize: 12, color: Color(0xFF475569), height: 1.5),
            )),
          ]),
          if (_error.isNotEmpty)
            Container(
              margin: const EdgeInsets.only(top: 8), padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(8), border: Border.all(color: const Color(0xFFFECACA))),
              child: Text(_error, style: const TextStyle(color: Color(0xFF991B1B), fontSize: 13)),
            ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: kAccent, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
              onPressed: _loading ? null : _submit,
              child: _loading
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                  : const Text('Submit Anonymous Report', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(height: 24),
        ]),
      ),
    );
  }

  Widget _privacyCard() => Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: const Color(0xFFF0FDF4), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFBBF7D0))),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('Your Privacy', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: kSuccess)),
      const SizedBox(height: 6),
      ...<String>['No name or contact info stored', 'Only aggregated statistics shared', 'Used for policy research only'].map((t) =>
        Padding(padding: const EdgeInsets.only(bottom: 3), child: Row(children: [
          const Icon(Icons.check, color: kSuccess, size: 13),
          const SizedBox(width: 5),
          Text(t, style: const TextStyle(fontSize: 12, color: Color(0xFF166534))),
        ])),
      ),
    ]),
  );

  Widget _lbl(String t) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Text(t.toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: Color(0xFF475569), letterSpacing: .5)),
  );

  Widget _chips(List<String> opts, String sel, void Function(String) onTap) => Wrap(
    spacing: 6, runSpacing: 6,
    children: opts.map((o) {
      final a = o == sel;
      return GestureDetector(
        onTap: () => onTap(o),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(color: a ? kPrimary : Colors.white, borderRadius: BorderRadius.circular(6), border: Border.all(color: a ? kPrimary : const Color(0xFFE2E8F0))),
          child: Text(o, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: a ? Colors.white : const Color(0xFF475569))),
        ),
      );
    }).toList(),
  );

  Widget _biasChips() => Wrap(
    spacing: 6, runSpacing: 6,
    children: _biasTypes.map((bt) {
      final a = bt == _biasType;
      final c = _biasColors[bt] ?? kPrimary;
      return GestureDetector(
        onTap: () => setState(() => _biasType = bt),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(color: a ? c : Colors.white, borderRadius: BorderRadius.circular(6), border: Border.all(color: a ? c : const Color(0xFFE2E8F0))),
          child: Text(bt, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: a ? Colors.white : const Color(0xFF475569))),
        ),
      );
    }).toList(),
  );
}

class _SuccessView extends StatelessWidget {
  final Map<String, dynamic> result;
  final VoidCallback onReset;
  const _SuccessView({required this.result, required this.onReset});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBg,
      appBar: AppBar(title: const Text('Report Submitted')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(children: [
          Container(
            width: 72, height: 72,
            decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(36)),
            child: const Icon(Icons.check, color: kSuccess, size: 36),
          ),
          const SizedBox(height: 16),
          const Text('Thank you for reporting', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: kPrimary)),
          const SizedBox(height: 6),
          Text('Report ID: ${result['report_id'] ?? ''}', style: const TextStyle(fontSize: 12, color: Color(0xFF475569), fontFamily: 'monospace')),
          if (result['preliminary_assessment'] != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: kBg, borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFE2E8F0))),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('AI Assessment', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: kPrimary)),
                const SizedBox(height: 8),
                Text(result['preliminary_assessment'] as String, style: const TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.6)),
              ]),
            ),
          ],
          if ((result['resources'] as List?)?.isNotEmpty ?? false) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFE2E8F0))),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Grievance Resources', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: kPrimary)),
                const SizedBox(height: 10),
                ...(result['resources'] as List).map((r) {
                  final res = r as Map<String, dynamic>;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: GestureDetector(
                      onTap: () { final url = res['url'] as String?; if (url != null) launchUrl(Uri.parse(url)); },
                      child: Row(children: [
                        const Icon(Icons.open_in_new, size: 13, color: Color(0xFF2563EB)),
                        const SizedBox(width: 6),
                        Expanded(child: Text(res['name'] as String? ?? '', style: const TextStyle(fontSize: 13, color: Color(0xFF2563EB), decoration: TextDecoration.underline))),
                      ]),
                    ),
                  );
                }),
              ]),
            ),
          ],
          const SizedBox(height: 20),
          SizedBox(width: double.infinity, child: OutlinedButton(onPressed: onReset, child: const Text('Submit Another Report'))),
        ]),
      ),
    );
  }
}

// ── Map Page ──────────────────────────────────────────────────────────────────
class MapPage extends StatelessWidget {
  const MapPage({super.key});

  static const _cities = [
    {'name': 'Delhi',      'count': 142, 'type': 'caste',    'domain': 'hiring'},
    {'name': 'Mumbai',     'count': 118, 'type': 'gender',   'domain': 'lending'},
    {'name': 'Bengaluru',  'count': 97,  'type': 'caste',    'domain': 'hiring'},
    {'name': 'Hyderabad',  'count': 71,  'type': 'religion', 'domain': 'hiring'},
    {'name': 'Chennai',    'count': 63,  'type': 'caste',    'domain': 'education'},
    {'name': 'Kolkata',    'count': 55,  'type': 'religion', 'domain': 'hiring'},
    {'name': 'Pune',       'count': 48,  'type': 'gender',   'domain': 'hiring'},
    {'name': 'Ahmedabad',  'count': 41,  'type': 'religion', 'domain': 'lending'},
    {'name': 'Jaipur',     'count': 39,  'type': 'caste',    'domain': 'healthcare'},
    {'name': 'Lucknow',    'count': 37,  'type': 'caste',    'domain': 'hiring'},
    {'name': 'Guwahati',   'count': 24,  'type': 'region',   'domain': 'hiring'},
    {'name': 'Chandigarh', 'count': 26,  'type': 'gender',   'domain': 'hiring'},
    {'name': 'Imphal',     'count': 14,  'type': 'region',   'domain': 'hiring'},
    {'name': 'Ranchi',     'count': 16,  'type': 'caste',    'domain': 'education'},
  ];

  static const _biasColors = {
    'caste': kAccent, 'religion': Color(0xFF7C3AED),
    'gender': Color(0xFF0891B2), 'region': kWarning,
  };

  Color _colorFor(String t) => _biasColors[t] ?? Colors.grey;

  @override
  Widget build(BuildContext context) {
    final totals = <String, int>{};
    for (final c in _cities) { totals[c['type'] as String] = (totals[c['type'] as String] ?? 0) + (c['count'] as int); }

    return Scaffold(
      backgroundColor: kBg,
      appBar: AppBar(
        title: const Text('India AI Bias Map'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(32),
          child: Container(padding: const EdgeInsets.only(left: 16, bottom: 8), alignment: Alignment.centerLeft,
            child: const Text('AGGREGATED ANONYMOUS COMMUNITY DATA', style: TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 1))),
        ),
      ),
      body: Column(children: [
        // Legend
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          color: Colors.white,
          child: Row(children: _biasColors.entries.map((e) => Padding(
            padding: const EdgeInsets.only(right: 14),
            child: Row(children: [
              Container(width: 8, height: 8, decoration: BoxDecoration(color: e.value, borderRadius: BorderRadius.circular(4))),
              const SizedBox(width: 5),
              Text(e.key, style: const TextStyle(fontSize: 11, color: Color(0xFF475569), fontWeight: FontWeight.w600)),
            ]),
          )).toList()),
        ),
        // Summary
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          color: const Color(0xFFF8FAFC),
          child: Row(children: totals.entries.map((e) => Expanded(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 3), padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8), border: Border(top: BorderSide(color: _colorFor(e.key), width: 3))),
              child: Column(children: [
                Text('${e.value}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _colorFor(e.key))),
                Text(e.key, style: const TextStyle(fontSize: 10, color: Color(0xFF475569))),
              ]),
            ),
          )).toList()),
        ),
        // City list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(14),
            itemCount: _cities.length,
            itemBuilder: (ctx, i) {
              final city = _cities[i];
              final count = city['count'] as int;
              final type = city['type'] as String;
              final color = _colorFor(type);
              return Container(
                margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white, borderRadius: BorderRadius.circular(12),
                  border: Border(left: BorderSide(color: color, width: 4), top: const BorderSide(color: Color(0xFFE2E8F0)), right: const BorderSide(color: Color(0xFFE2E8F0)), bottom: const BorderSide(color: Color(0xFFE2E8F0))),
                ),
                child: Row(children: [
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(city['name'] as String, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: kPrimary)),
                    const SizedBox(height: 2),
                    Text('${city['domain']} - ${city['type']} bias', style: const TextStyle(fontSize: 12, color: Color(0xFF475569))),
                  ])),
                  Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                    Text('$count', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: color, letterSpacing: -1)),
                    const Text('reports', style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8))),
                  ]),
                ]),
              );
            },
          ),
        ),
      ]),
    );
  }
}
