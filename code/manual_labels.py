"""Labels (made by reading each name, as part of the AI-assisted analysis, and reviewed by the author) for the random accuracy sample (data/_sample_names.csv: 300 takeaways and
150 restaurants, drawn with random.seed(20261028)). Each name was read on its own, without the
classifier's answer, and given the family its name plainly points to, or "unknown" when the name
alone does not say. Where a name names two foods ("Chicken & Pizza") both are listed with "|" and
either counts as right. Knowledge of well-known chains and of a few regional names was allowed.
"""
L = """
0 fish_chips;1 pizza;2 fish_chips;3 unknown;4 chinese;5 unknown;6 burger;7 chinese;8 sandwich;9 chicken|pizza;
10 kebab;11 pizza;12 fish_chips;13 unknown;14 chinese;15 unknown;16 fish_chips;17 chicken;18 sandwich;19 pizza;
20 chinese;21 chicken;22 fish_chips;23 chinese;24 pizza;25 unknown;26 unknown;27 unknown;28 unknown;29 chinese;
30 cafe;31 unknown;32 sandwich;33 chicken;34 fish_chips;35 fish_chips;36 chinese;37 chicken|pizza;38 caribbean;39 kebab;
40 cafe;41 fish_chips;42 indian;43 unknown;44 sandwich;45 unknown;46 unknown;47 unknown;48 caribbean;49 sandwich;
50 chinese;51 cafe;52 chinese;53 chicken;54 unknown;55 indian;56 fish_chips;57 chinese;58 indian;59 chinese;
60 chinese;61 kebab;62 unknown;63 unknown;64 cafe;65 sandwich;66 unknown;67 pizza|fish_chips;68 fish_chips;69 sandwich;
70 sandwich;71 sandwich;72 cafe;73 burger;74 unknown;75 kebab;76 pizza;77 fish_chips;78 kebab;79 indian;
80 unknown;81 unknown;82 chinese;83 unknown;84 pizza;85 sandwich;86 chinese;87 unknown;88 fish_chips;89 unknown;
90 pizza;91 chinese;92 unknown;93 pizza;94 unknown;95 unknown;96 cafe;97 chicken;98 chicken;99 kebab;
100 unknown;101 kebab|pizza;102 cafe;103 cafe;104 chinese;105 unknown;106 chinese;107 unknown;108 chicken;109 chinese;
110 unknown;111 unknown;112 unknown;113 chinese;114 chinese;115 sandwich;116 pizza;117 fish_chips;118 japanese;119 fish_chips|kebab;
120 unknown;121 unknown;122 pizza;123 pizza;124 cafe;125 unknown;126 chinese;127 caribbean;128 sandwich;129 chinese;
130 chicken;131 chinese;132 japanese;133 unknown;134 unknown;135 fish_chips;136 cafe;137 unknown;138 japanese;139 chicken;
140 cafe;141 unknown;142 unknown;143 fish_chips;144 pizza;145 unknown;146 indian;147 unknown;148 pizza|indian;149 sandwich;
150 sandwich;151 unknown;152 pizza;153 chicken|burger;154 pizza;155 pizza;156 unknown;157 asian_other;158 kebab;159 unknown;
160 pizza;161 fish_chips;162 chicken;163 cafe;164 unknown;165 sandwich|cafe;166 fish_chips;167 cafe;168 chinese;169 cafe;
170 chinese;171 unknown;172 fish_chips;173 fish_chips;174 pizza;175 chinese;176 pizza;177 chicken;178 chinese;179 unknown;
180 unknown;181 unknown;182 fish_chips|kebab;183 unknown;184 chinese;185 chicken|cafe;186 sandwich;187 italian|pizza;188 chicken;189 unknown;
190 pizza;191 unknown;192 chicken;193 unknown;194 unknown;195 cafe;196 chinese;197 unknown;198 chinese;199 unknown;
200 pizza;201 sandwich;202 kebab;203 pizza;204 unknown;205 unknown;206 unknown;207 unknown;208 sandwich;209 pizza|chicken;
210 chicken;211 chinese;212 sandwich;213 cafe;214 chinese;215 unknown;216 fish_chips|chicken;217 kebab;218 indian;219 pizza;
220 cafe;221 chinese;222 pizza;223 chicken|pizza;224 indian;225 chinese;226 fish_chips;227 sandwich;228 sandwich;229 chicken|pizza;
230 japanese;231 cafe;232 unknown;233 unknown;234 unknown;235 pizza|indian;236 greek_med;237 unknown;238 kebab;239 burger;
240 unknown;241 unknown;242 fish_chips;243 unknown;244 pizza;245 sandwich;246 unknown;247 chinese;248 indian;249 indian;
250 fish_chips;251 chinese;252 pizza|kebab;253 fish_chips;254 kebab;255 unknown;256 unknown;257 chinese;258 fish_chips;259 asian_other|chinese;
260 italian;261 unknown;262 chinese;263 indian;264 cafe;265 unknown;266 fish_chips;267 pizza;268 chinese;269 sandwich;
270 sandwich;271 kebab;272 unknown;273 chicken;274 cafe;275 sandwich;276 chinese;277 burger;278 unknown;279 unknown;
280 fish_chips;281 unknown;282 sandwich;283 chicken;284 unknown;285 sandwich;286 sandwich;287 unknown;288 unknown;289 unknown;
290 unknown;291 chinese;292 kebab;293 unknown;294 chinese|chicken;295 cafe;296 unknown;297 cafe;298 chicken;299 cafe;
300 unknown;301 sandwich;302 unknown;303 unknown;304 unknown;305 cafe;306 cafe;307 unknown;308 cafe;309 unknown;
310 cafe;311 greek_med|kebab;312 unknown;313 burger|chicken;314 sandwich;315 cafe;316 cafe;317 unknown;318 chicken;319 indian;
320 unknown;321 cafe;322 unknown;323 cafe;324 unknown;325 unknown;326 unknown;327 unknown;328 chicken;329 unknown;
330 indian;331 indian;332 unknown;333 indian;334 unknown;335 unknown;336 unknown;337 unknown;338 cafe;339 unknown;
340 unknown;341 cafe|asian_other;342 sandwich;343 unknown;344 unknown;345 unknown;346 indian;347 unknown;348 chicken;349 unknown;
350 cafe;351 unknown;352 unknown;353 japanese;354 italian;355 unknown;356 sandwich;357 unknown;358 italian;359 unknown;
360 unknown;361 unknown;362 fish_chips;363 unknown;364 unknown;365 cafe;366 unknown;367 chicken;368 cafe;369 indian;
370 cafe;371 cafe;372 unknown;373 sandwich;374 sandwich;375 unknown;376 unknown;377 unknown;378 sandwich;379 unknown;
380 italian|pizza;381 unknown;382 unknown;383 indian;384 unknown;385 chinese;386 unknown;387 cafe;388 unknown;389 cafe;
390 unknown;391 unknown;392 unknown;393 unknown;394 unknown;395 unknown;396 unknown;397 unknown;398 cafe;399 unknown;
400 unknown;401 cafe;402 unknown;403 unknown;404 cafe;405 unknown;406 indian;407 unknown;408 unknown;409 unknown;
410 cafe;411 cafe;412 cafe;413 unknown;414 indian|cafe;415 cafe;416 unknown;417 unknown;418 unknown;419 unknown;
420 cafe;421 unknown;422 cafe;423 unknown;424 cafe;425 thai;426 sandwich|cafe;427 cafe;428 cafe;429 unknown;
430 indian;431 unknown;432 indian;433 unknown;434 chicken;435 mexican;436 cafe;437 burger;438 indian;439 cafe;
440 unknown;441 unknown;442 unknown;443 cafe;444 unknown;445 unknown;446 cafe;447 unknown;448 unknown;449 cafe
"""
LABELS = {}
for item in L.replace("\n", "").split(";"):
    item = item.strip()
    if item:
        k, v = item.split(" ", 1)
        LABELS[int(k)] = v.strip()
assert len(LABELS) == 450, len(LABELS)

# Held-out sample B (data/_sample_names_b.csv: 200 takeaways and 100 restaurants, random.seed(7202611),
# excluding sample A), drawn and labelled after the rules were last changed; its scores are the ones reported.
LB = """
0 indian;1 chinese;2 pizza;3 unknown;4 unknown;5 chinese;6 chicken;7 unknown;8 pizza;9 chicken;
10 unknown;11 fish_chips;12 kebab;13 fish_chips;14 indian;15 sandwich;16 sandwich;17 japanese;18 indian;19 unknown;
20 fish_chips;21 chinese;22 unknown;23 pizza;24 japanese;25 caribbean|chicken;26 chinese;27 unknown;28 pizza;29 sandwich;
30 burger;31 sandwich;32 indian;33 fish_chips;34 sandwich;35 fish_chips;36 thai;37 chicken;38 sandwich;39 chinese;
40 cafe;41 unknown;42 indian;43 fish_chips;44 unknown;45 unknown;46 burger;47 chinese;48 unknown;49 unknown;
50 cafe;51 chinese;52 fish_chips;53 unknown;54 unknown;55 chicken;56 kebab;57 indian;58 cafe;59 pizza;
60 burger;61 chinese;62 unknown;63 fish_chips;64 unknown;65 greek_med;66 pizza;67 unknown;68 unknown;69 sandwich;
70 pizza;71 chinese;72 unknown;73 unknown;74 fish_chips;75 chinese;76 chinese;77 unknown;78 unknown;79 indian;
80 indian;81 cafe;82 thai;83 unknown;84 chinese;85 unknown;86 chinese;87 chinese;88 chinese;89 unknown;
90 chicken;91 kebab;92 fish_chips;93 fish_chips;94 unknown;95 cafe;96 chinese;97 unknown;98 pizza;99 unknown;
100 chinese;101 cafe;102 chicken;103 thai;104 chinese;105 fish_chips;106 unknown;107 asian_other;108 fish_chips;109 unknown;
110 unknown;111 italian;112 unknown;113 cafe;114 fish_chips;115 unknown;116 sandwich;117 fish_chips;118 unknown;119 pizza;
120 cafe;121 unknown;122 unknown;123 chinese;124 fish_chips;125 unknown;126 pizza;127 unknown;128 chinese;129 chinese;
130 cafe;131 unknown;132 japanese;133 chicken;134 fish_chips;135 greek_med;136 fish_chips;137 unknown;138 fish_chips;139 fish_chips;
140 burger;141 cafe;142 pizza;143 unknown;144 chinese;145 fish_chips;146 unknown;147 unknown;148 unknown;149 unknown;
150 pizza;151 chicken;152 chinese;153 chinese;154 unknown;155 unknown;156 fish_chips;157 chicken;158 unknown;159 unknown;
160 indian;161 unknown;162 burger;163 cafe|indian;164 pizza;165 pizza;166 cafe;167 cafe;168 sandwich;169 sandwich;
170 pizza;171 pizza;172 unknown;173 burger;174 fish_chips;175 unknown;176 pizza;177 japanese;178 fish_chips;179 sandwich;
180 chinese;181 indian;182 sandwich;183 fish_chips;184 unknown;185 chinese;186 pizza;187 burger;188 unknown;189 pizza;
190 pizza|kebab;191 indian;192 fish_chips;193 kebab;194 cafe;195 unknown;196 kebab;197 fish_chips;198 burger;199 fish_chips;
200 unknown;201 indian;202 asian_other|indian;203 cafe;204 unknown;205 unknown;206 caribbean;207 cafe;208 cafe;209 unknown;
210 unknown;211 cafe;212 unknown;213 unknown;214 chinese;215 caribbean;216 cafe;217 cafe;218 unknown;219 unknown;
220 cafe;221 pizza;222 cafe;223 unknown;224 unknown;225 unknown;226 sandwich;227 cafe;228 sandwich;229 cafe;
230 unknown;231 burger;232 unknown;233 unknown;234 cafe;235 cafe;236 thai;237 cafe;238 indian;239 cafe;
240 unknown;241 japanese;242 unknown;243 unknown;244 unknown;245 unknown;246 cafe;247 unknown;248 indian;249 cafe;
250 unknown;251 cafe;252 cafe;253 unknown;254 burger;255 unknown;256 unknown;257 unknown;258 cafe|japanese;259 cafe;
260 cafe;261 unknown;262 unknown;263 cafe;264 cafe;265 unknown;266 caribbean;267 unknown;268 cafe;269 unknown;
270 chinese;271 cafe;272 unknown;273 cafe;274 unknown;275 unknown;276 unknown;277 unknown;278 unknown;279 unknown;
280 unknown;281 unknown;282 cafe|indian;283 japanese;284 cafe;285 cafe;286 unknown;287 cafe;288 unknown;289 unknown;
290 unknown;291 cafe;292 unknown;293 cafe;294 chinese|asian_other;295 unknown;296 unknown;297 unknown;298 cafe;299 unknown
"""
LABELS_B = {}
for item in LB.replace("\n", "").split(";"):
    item = item.strip()
    if item:
        k, v = item.split(" ", 1)
        LABELS_B[int(k)] = v.strip()
assert len(LABELS_B) == 300, len(LABELS_B)
