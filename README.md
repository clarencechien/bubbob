# bubbob — 強化版泡泡龍「蓄能引爆」手感原型

單一 `index.html`（vanilla JS + Canvas 2D，零相依、零 build），直接用瀏覽器打開即玩。
規格見 [SPEC.md](SPEC.md)（v0.2）。

## 玩法

- `←→` / `A D` 移動，`空白` / `↑` / `W` 跳，`J` / 滑鼠左鍵吐泡泡困敵
- **身體碰到敵泡泡＝引爆**，鄰近泡泡 BFS 連鎖
- 泡泡越熟價值越高、掙脫機率也越高：綠 ×1 → 黃 ×2 → 橙 ×3.5 → 紅閃 ×6
- 引爆獎勵依 Tier：綠＝純分數、黃＝補血、橙＝雙泡能力、紅＝無敵星（碰敵自動困成泡泡）
- 被敵人碰到扣 1 血（預設 5 血，可調），歸零即崩盤結束
- 右側面板：難易度一鍵預設（簡單／中等／最難）＋ 9 顆即時滑桿，`escapeRate` 是主旋鈕

## 素材

像素素材取自 [KAPLAY](https://github.com/kaplayjs/kaplay) crew sprites（MIT License, © KAPLAY Team），
以 base64 內嵌。面板的素材槽可上傳圖片即時替換玩家／敵人／暴走敵／泡泡，
squash & stretch、Tier 著色、閃爍等效果照常套用。
