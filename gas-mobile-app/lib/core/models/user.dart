class GASUser {
  final String id;
  final String email;
  final String fullName;
  final String? avatarUrl;
  final String plan;
  final int credits;
  final int xp;
  final int level;
  final String levelName;
  final bool isAdmin;
  final String? role;
  final DateTime? createdAt;
  final DateTime? lastLogin;

  const GASUser({
    required this.id,
    required this.email,
    required this.fullName,
    this.avatarUrl,
    required this.plan,
    required this.credits,
    required this.xp,
    required this.level,
    required this.levelName,
    required this.isAdmin,
    this.role,
    this.createdAt,
    this.lastLogin,
  });

  factory GASUser.fromJson(Map<String, dynamic> j) => GASUser(
    id:        j['id']?.toString() ?? '',
    email:     j['email'] as String? ?? '',
    fullName:  j['full_name'] as String? ?? j['name'] as String? ?? '',
    avatarUrl: j['avatar_url'] as String?,
    plan:      j['plan'] as String? ?? 'essential',
    credits:   (j['credits'] as num?)?.toInt() ?? 0,
    xp:        (j['xp'] as num?)?.toInt() ?? 0,
    level:     (j['level'] as num?)?.toInt() ?? 1,
    levelName: j['level_name'] as String? ?? 'Rookie',
    isAdmin:   j['is_admin'] as bool? ?? j['role'] == 'admin',
    role:      j['role'] as String?,
    createdAt: j['created_at'] != null
        ? DateTime.tryParse(j['created_at'] as String) : null,
    lastLogin: j['last_login'] != null
        ? DateTime.tryParse(j['last_login'] as String) : null,
  );

  Map<String, dynamic> toJson() => {
    'id':          id,
    'email':       email,
    'full_name':   fullName,
    'avatar_url':  avatarUrl,
    'plan':        plan,
    'credits':     credits,
    'xp':          xp,
    'level':       level,
    'level_name':  levelName,
    'is_admin':    isAdmin,
    'role':        role,
  };

  GASUser copyWith({
    String? fullName,
    String? avatarUrl,
    String? plan,
    int? credits,
    int? xp,
    int? level,
    String? levelName,
  }) => GASUser(
    id:        id,
    email:     email,
    fullName:  fullName  ?? this.fullName,
    avatarUrl: avatarUrl ?? this.avatarUrl,
    plan:      plan      ?? this.plan,
    credits:   credits   ?? this.credits,
    xp:        xp        ?? this.xp,
    level:     level     ?? this.level,
    levelName: levelName ?? this.levelName,
    isAdmin:   isAdmin,
    role:      role,
    createdAt: createdAt,
    lastLogin: lastLogin,
  );
}
