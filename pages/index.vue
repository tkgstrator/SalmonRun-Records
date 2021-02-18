<template>
  <div class="page coop-blacklist">
    <header class="navigation-bar">
      <h1>
        Unofficial Salmon Run Site
      </h1>
    </header>
    <div class="coop-blacklist-header">
      <h2><span>Salmon Run</span></h2>
      <h3><span>Warning Players List</span></h3>
    </div>
    <div class="coop-blacklist-wrapper">
      <div id="coop-blacklist-players"></div>
    </div>
  </div>
</template>

<script>
import players from "@/assets/json/lanplay.json"

const keys = ["thumbnail_url", "nickname", "banned_reason"]

export default {
  data() {
    return {
      players: players
    }
  },
  async mounted() {
    // テーブルを作成する
    var table = document.createElement("table")
    // ヘッダーを作成する
    var tr = document.createElement("tr")
    var thead = document.createElement("thead")

    keys.forEach(key => {
      var th = document.createElement("th")
      th.className = key
      th.textContent = key
      thead.appendChild(th)
    })
      table.appendChild(thead)

    players.forEach(player => {
      var tr = document.createElement("tr")
      // まずはアイコン
      var td = document.createElement("td")
      td.className = "thumbnail_url"
      var img = document.createElement("img")
      img.src = player["thumbnail_url"]
      td.appendChild(img)
      tr.appendChild(td)

      // プレイヤー名
      var td = document.createElement("td")
      td.className = "nickname"
      var name = document.createElement("p")
      name.textContent = player["nickname"]
      td.appendChild(name)
      tr.appendChild(td)

      // BANの理由
      var td = document.createElement("td")
      var reason = document.createElement("p")
      td.className = "banned_reason"
      reason.textContent = "Cheating"
      td.appendChild(reason)
      tr.appendChild(td)
      table.appendChild(tr)
    });

    document.getElementById("coop-blacklist-players").appendChild(table)
  }
};
</script>

<style lang="scss">
@import "~assets/sass/style.scss";
// @import "~assets/sass/splatnet2.scss";
@import "~assets/sass/blacklist.scss";
</style>