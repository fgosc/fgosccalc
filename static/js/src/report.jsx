"use strict";
// ver 20200801-01
Sentry.init({
  dsn: "https://c3ee02d195ae440aacd020b5869abfa7@o425638.ingest.sentry.io/5363673",
});

// https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/set-up-twitter-for-websites
window.twttr = (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0],
    t = window.twttr || {};
  if (d.getElementById(id)) return;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);

  t._e = [];
  t.ready = function(f) {
    t._e.push(f);
  };

  return t;
}(document, "script", "twitter-wjs"));

const defaultQuestName = '(クエスト名)'
const tweetURL = 'https://fgosccalc.appspot.com'

class TableLine extends React.Component {
  constructor(props) {
    super(props)

    this.handleMaterialChange = this.handleMaterialChange.bind(this)
    this.handleAddChange = this.handleAddChange.bind(this)
    this.handleReduceChange = this.handleReduceChange.bind(this)
    this.handleReportChange = this.handleReportChange.bind(this)
    this.handleEditClick = this.handleEditClick.bind(this)
    this.handleDiscardEditClick = this.handleDiscardEditClick.bind(this)
    this.handleDeleteClick = this.handleDeleteClick.bind(this)
    this.handleUpClick = this.handleUpClick.bind(this)
    this.handleDownClick = this.handleDownClick.bind(this)

    this.state = {
      editResult: false,
    }
  }

  handleMaterialChange(event) {
    this.props.onMaterialChange(this.props.id, event.target.value)
  }

  handleAddChange(event) {
    this.props.onMaterialAddCountChange(this.props.id, event.target.value)
  }

  handleReduceChange(event) {
    this.props.onMaterialReduceCountChange(this.props.id, event.target.value)
  }

  handleReportChange(event) {
    this.props.onMaterialReportCountChange(this.props.id, event.target.value)
  }

  handleEditClick(event) {
    this.setState({ editResult: true })
    // 直接入力開始時は今までの増減操作をなかったことにする
    this.props.onMaterialAddCountChange(this.props.id, 0)
    this.props.onMaterialReduceCountChange(this.props.id, 0)
  }

  handleDiscardEditClick(event) {
    this.setState({ editResult: false })
    // 直接入力終了時は今までの編集操作をなかったことにする
    this.props.onMaterialReportCountChange(this.props.id, this.props.initial)
  }

  handleDeleteClick(event) {
    if (confirm("この行を削除しますか？")) {
      this.props.onLineDeleteButtonClick(this.props.id)
    }
  }

  handleUpClick(event) {
    this.props.onLineUpButtonClick(this.props.id)
  }

  handleDownClick(event) {
    this.props.onLineDownButtonClick(this.props.id)
  }

  isValidMaterialValue(v) {
    if (v === '') {
      return 'BLANK'
    }
    if (v === '!') {
      return 'BLANK'
    }
    if (/[0-9]/.test(v[v.length-1])) {
      return 'TAILNUM'
    }
    return 'OK'
  }

  isValidReportValue(v) {
    const s = String(v).trim()
    if (s === "NaN") {
      return true
    }
    if (!/^[0-9]+$/.test(s)) {
      return false
    }
    if (s !== '0' && s.startsWith('0')) {
      // 012 のような記述を排除する目的
      return false
    }
    return true
  }

  render() {
    // TODO refactor
    let materialComponent, addComponent, reduceComponent, reportComponent, editButton
    const materialValue = this.props.material
    const reportValue = this.props.report

    const materialValidationResult = this.isValidMaterialValue(materialValue.trim())
    if (materialValidationResult === 'BLANK') {
      materialComponent = (
        <React.Fragment>
          <input type="text" className="input is-small is-danger" value={materialValue} onChange={this.handleMaterialChange} />
          <p className="help is-danger">入力必須</p>
        </React.Fragment>
      )
    } else if (materialValidationResult === 'TAILNUM') {
      materialComponent = (
        <React.Fragment>
          <input type="text" className="input is-small" value={materialValue} onChange={this.handleMaterialChange} />
          <p className="help is-danger">末尾は数字以外</p>
        </React.Fragment>
      )
    } else {
      materialComponent = <input type="text" className="input is-small" value={materialValue} onChange={this.handleMaterialChange} />
    }

    if (this.state.editResult) {
      addComponent = <span>{this.props.add}</span>
      reduceComponent = <span>{this.props.reduce}</span>
      if (!this.isValidReportValue(reportValue)) {
        reportComponent = (
          <React.Fragment>
            <input type="text" className="input is-small is-danger" value={reportValue} onChange={this.handleReportChange} />
            <p className="help is-danger">整数または NaN</p>
          </React.Fragment>
        )
      } else {
        reportComponent = <input type="text" className="input is-small" value={reportValue} onChange={this.handleReportChange} />
      }
      editButton = <button className="button is-small is-danger" onClick={this.handleDiscardEditClick}>キャンセル</button>
    } else {
      addComponent = <input type="number" className="input is-small" min="0" value={this.props.add} onChange={this.handleAddChange} />
      reduceComponent = <input type="number" className="input is-small" min="0" value={this.props.reduce} onChange={this.handleReduceChange} />
      reportComponent = <span>{reportValue}</span>
      editButton = <button className="button is-small is-success" onClick={this.handleEditClick}>直接入力</button>
    }

    return (
      <tr>
        <td className="valign-middle">
          <button className="button is-small" onClick={this.handleDeleteClick}>
            <i className="fas fa-trash"></i>
          </button>
          <button className="button is-small" onClick={this.handleUpClick}>
            <i className="fas fa-arrow-up"></i>
          </button>
          <button className="button is-small" onClick={this.handleDownClick}>
            <i className="fas fa-arrow-down"></i>
          </button>
        </td>
        <td className="valign-middle">
          {materialComponent}
        </td>
        <td className="valign-middle">
          {this.props.initial}
        </td>
        <td className="valign-middle">
          {addComponent}
        </td>
        <td className="valign-middle">
          {reduceComponent}
        </td>
        <td className="valign-middle">
          {reportComponent}
        </td>
        <td className="valign-middle">
          {editButton}
        </td>
      </tr>
    )
  }
}
  
class Table extends React.Component {
  render() {
    return (
      <div style={{marginBottom: 1.5 + 'rem'}}>
        <table className="is-narrow">
          <thead>
            <tr>
              <th></th>
              <th>素材名</th>
              <th>解析結果</th>
              <th>消費</th>
              <th>追加獲得</th>
              <th>報告値</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
          {this.props.lines.map((e) => {
            return (
              <TableLine key={e.id}
                {...e}
                onMaterialChange={this.props.onMaterialChange}
                onMaterialAddCountChange={this.props.onMaterialAddCountChange}
                onMaterialReduceCountChange={this.props.onMaterialReduceCountChange}
                onMaterialReportCountChange={this.props.onMaterialReportCountChange}
                onLineDeleteButtonClick={this.props.onLineDeleteButtonClick}
                onLineUpButtonClick={this.props.onLineUpButtonClick}
                onLineDownButtonClick={this.props.onLineDownButtonClick}
              />)
          })}
          </tbody>
        </table>
        <div>
          <button className="button is-small" onClick={this.props.onAddRowButtonClick}><i className="fas fa-plus"></i></button>
        </div>
        <ul class="note">
          <li><b>消費</b> ... 解析結果に指定した数を加えて報告数を増やします。たとえば、周回カウント中に育成等で素材を消費した場合など。</li>
          <li><b>追加獲得</b> ... 解析結果から指定した数を引いて報告数を減らします。たとえば、周回以外で入手した素材を集計から除外したいなど。</li>
          <li><b>直接入力</b> ... 解析結果を無視して報告数を直接入力します。解析結果が正しくない場合や、解析ではカウント不可能なアイテム（礼装や種火など）の報告に使います。</li>
        </ul>
      </div>
    )
  }
}

class QuestNameEditor extends React.Component {
  constructor(props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
  }

  handleChange(event) {
    this.props.onQuestNameChange(event.target.value)
  }

  buildInputNode(questname) {
    if (questname === defaultQuestName || questname.trim().length === 0) {
      return (
        <div className="control">
          <input type="text" className="input is-small is-danger" value={questname} onChange={this.handleChange} />
          <p className="help is-danger">周回場所を入力してください。</p>
        </div>
      )
    }
    const pos = questname.replace(/　/g, ' ').trim().indexOf(' ')
    if (pos < 0) {
      return (
        <div className="control">
          <input type="text" className="input is-small is-info" value={questname} onChange={this.handleChange} />
          <p className="help is-info">「剣の修練場 超級」「オケアノス 豊かな海」のようにスペースで区切る記述を推奨します。</p>
        </div>
      )
    }
    return (
      <div className="control has-icons-right">
        <input type="text" className="input is-small is-success" value={questname} onChange={this.handleChange} />
        <span class="icon is-small is-right">
          <i class="fas fa-check"></i>
        </span>
      </div>
    )
  }

  render() {
    const questname = this.props.questname
    const node = this.buildInputNode(questname)
    return (
      <div className="field">
        <label className="label">周回場所</label>
        {node}
      </div>
    )
  }
}

class RunCountEditor extends React.Component {
  constructor(props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.addValue = this.addValue.bind(this)
    this.handleClick = this.handleClick.bind(this)
  }

  handleChange(event) {
    this.props.onRunCountChange(event.target.value)
  }

  addValue(delta) {
    let runcount = parseInt(this.props.runcount)
    // ブランクなど数値でない場合に NaN になる可能性がある。
    // その場合は強制的に 0 にする。
    if (isNaN(runcount)) {
      runcount = 0
    }
    let v = runcount + delta
    if (v < 0) {
      v = 0
    }
    this.props.onRunCountChange(v)
  }

  buildInputNode(runcount) {
    const _runcount = parseInt(runcount)
    if (_runcount <= 0 || isNaN(_runcount)) {
      return (
        <div className="control">
          <input type="number" className="input is-small is-danger" min="0" value={this.props.runcount} onChange={this.handleChange} />
          <p className="help is-danger">周回数を設定してください。</p>
        </div>
      )
    }
    return (
      <div className="control has-icons-right">
        <input type="number" className="input is-small is-success" min="0" value={this.props.runcount} onChange={this.handleChange} />
        <span class="icon is-small is-right">
          <i class="fas fa-check"></i>
        </span>
      </div>
    )
  }

  handleClick(event) {
    this.addValue(parseInt(event.target.textContent))
  }

  render() {
    const runcount = this.props.runcount
    const inputNode = this.buildInputNode(runcount)
    return (
      <div>
        <div className="field">
          <label className="label">周回数</label>
          {inputNode}
        </div>
        <div className="buttons">
            <button className="button is-small is-danger" onClick={this.handleClick}>-1000</button>
            <button className="button is-small is-danger" onClick={this.handleClick}>-100</button>
            <button className="button is-small is-danger" onClick={this.handleClick}>-10</button>
            <button className="button is-small is-danger" onClick={this.handleClick}>-1</button>
            <button className="button is-small is-link" onClick={this.handleClick}>+1</button>
            <button className="button is-small is-link" onClick={this.handleClick}>+10</button>
            <button className="button is-small is-link" onClick={this.handleClick}>+100</button>
            <button className="button is-small is-link" onClick={this.handleClick}>+1000</button>
        </div>
      </div>
    )
  }
}

class ReportViewer extends React.Component {
  computeRows(rows) {
    // TODO あまり洗練された手法とはいえない
    const screenWidth = window.screen.width

    const overflows = rows.filter(r => {
      if (screenWidth < 376) {
        return r.length > 30
      } else if (screenWidth < 414) {
        return r.length > 35
      }
      return false
    }).length

    return rows.length + overflows
  }
  render() {
    const rows = this.props.reportText.split('\n')
    const numRows = this.computeRows(rows)

    return (
      <div className="field">
        <label className="label">
          周回報告テキスト
          <span className="tag is-warning">直接編集不可</span>
        </label>
        <div className="control">
          <textarea className="textarea is-small" style={{backgroundColor: "#fffbeb"}} readOnly value={this.props.reportText} rows={numRows} />
        </div>
      </div>
    )
  }
}

class TweetButton extends React.Component {
  constructor(props) {
    super(props)
    this.createTweetButton = this.createTweetButton.bind(this)
    this.state = { tweetButtonDisplayed: false }
  }

  isValidCondition(questname, runcount) {
    // questname
    if (questname === defaultQuestName) {
      return false
    }
    if (questname.trim().length === 0) {
      return false
    }
    // runcount
    if (runcount <= 0) {
      return false
    }
    return true
  }

  removeTweetButton() {
    console.log('removeTweetButton event')
    const el = document.getElementById('tweet-button')
    if (el === null) {
      return
    }
    for (let node of el.childNodes) {
      el.removeChild(node)
    }
    this.setState({ tweetButtonDisplayed: false })
  }

  createTweetButton(event) {
    console.log('createShareButton event')
    // tweet-button はこのコンテナの外にある
    const el = document.getElementById('tweet-button')
    if (el === null) {
      return
    }

    console.log('ready')
    window.twttr.ready(() => {
      for (let node of el.childNodes) {
        el.removeChild(node)
      }
      console.log('createShareButton run')
      window.twttr.widgets.createShareButton(
        tweetURL,
        el,
        {
          text: this.props.reportText,
          size: 'large',
        }
      )
      console.log('createShareButton ok')
      this.props.onShowTweetButton()
      this.setState({ tweetButtonDisplayed: true })
    })
  }

  render() {
    const tweetButtonDisplayed = this.state.tweetButtonDisplayed
    if (tweetButtonDisplayed && this.props.canTweet != tweetButtonDisplayed) {
      // 上位コンポーネントがツイートボタン表示不可といっているので、その状態に合わせる。
      // このような回りくどいことをしているのは DOM 操作が絡むから。
      this.removeTweetButton()
    }
    const invalidCondition = !this.isValidCondition(this.props.questname, this.props.runcount)
    let className
    if (invalidCondition) {
      className = "button is-small"
    } else {
      className = "button is-small is-link"
    }
    const generateButton = <button className={className} disabled={invalidCondition} onClick={this.createTweetButton}>ツイートボタン生成</button>
    return (
      <div style={{ marginTop: 1 + 'rem'}}>
        {generateButton}
      </div>
    )
  }
}

class EditBox extends React.Component {
  constructor(props) {
    super(props)

    this.handleEditClick = this.handleEditClick.bind(this)
    this.handleCloseClick = this.handleCloseClick.bind(this)
    this.handleQuestNameChange = this.handleQuestNameChange.bind(this)
    this.handleRunCountChange = this.handleRunCountChange.bind(this)
    this.handleMaterialChange = this.handleMaterialChange.bind(this)
    this.handleMaterialAddCountChange = this.handleMaterialAddCountChange.bind(this)
    this.handleMaterialReduceCountChange = this.handleMaterialReduceCountChange.bind(this)
    this.handleMaterialReportCountChange = this.handleMaterialReportCountChange.bind(this)
    this.handleLineDeleteButtonClick = this.handleLineDeleteButtonClick.bind(this)
    this.handleLineUpButtonClick = this.handleLineUpButtonClick.bind(this)
    this.handleLineDownButtonClick = this.handleLineDownButtonClick.bind(this)
    this.handleAddRowButtonClick = this.handleAddRowButtonClick.bind(this)
    this.buildReportText = this.buildReportText.bind(this)
    this.handleShowTweetButton = this.handleShowTweetButton.bind(this)

    const questname = props.questname
    const runcount = parseInt(props.runcount)
    const lines = props.lines
    const image_url = props.image_url

    lines.map(line => {
      // report の値を計算しておく。
      // data から与えられた report 値はここで上書きしてしまってよい。
      line.report = this.computeReportValue(line)
    })

    this.state = {
      editMode: false,
      questname: questname,
      runcount: runcount,
      lines: lines,
      image_url: image_url,
      reportText: this.buildReportText(questname, runcount, lines, image_url),
      canTweet: false,
    }
  }

  handleEditClick(event) {
    this.setState({ editMode: true })
  }

  handleCloseClick(event) {
    this.setState({ editMode: false })
  }

  handleQuestNameChange(questname) {
    this.setState((state) => ({
        questname: questname,
        reportText: this.buildReportText(questname, state.runcount, state.lines, state.image_url),
        canTweet: false,
    }))
  }

  handleRunCountChange(runcount) {
    this.setState((state) => ({
      runcount: runcount,
      reportText: this.buildReportText(state.questname, runcount, state.lines, state.image_url),
      canTweet: false,
    }))
  }

  rebuildLines(lines, hook, triggerLineId) {
    let newlines = [];
    for (let line of lines) {
      if (line.id === triggerLineId) {
        hook(line)
      }
      newlines.push(line);
    }
    return newlines
  }

  handleMaterialChange(id, material) {
    const hook = (line) => {
      line.material = material
    }
    const newlines = this.rebuildLines(this.state.lines, hook, id)
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines, state.image_url),
      canTweet: false,
    }))
  }

  computeReportValue(line) {
    let reportValue = parseInt(line.initial) + parseInt(line.add) - parseInt(line.reduce)
    if (reportValue < 0 || isNaN(reportValue)) {
      reportValue = "NaN"
    }
    return reportValue
  }

  handleMaterialAddCountChange(id, count) {
    const hook = (line) => {
      line.add = count
      line.report = this.computeReportValue(line)
    }
    const newlines = this.rebuildLines(this.state.lines, hook, id)
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines, state.image_url),
      canTweet: false,
    }))
  }

  handleMaterialReduceCountChange(id, count) {
    const hook = (line) => {
      line.reduce = count
      line.report = this.computeReportValue(line)
    }
    const newlines = this.rebuildLines(this.state.lines, hook, id)
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines, state.image_url),
      canTweet: false,
    }))
  }

  handleMaterialReportCountChange(id, count) {
    const hook = (line) => {
      if (count < 0) {
        line.report = "NaN"
      } else {
        line.report = count
      }
    }
    const newlines = this.rebuildLines(this.state.lines, hook, id)
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines, state.image_url),
      canTweet: false,
    }))
  }

  handleLineDeleteButtonClick(id) {
    const newlines = this.state.lines.filter(line => { return line.id !== id })
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines, state.image_url),
      canTweet: false,
    }))
  }

  findAboveLine(lines, target) {
    return lines.reduce((currentMax, line) => {
      // target よりも order が小さく、かつ最大の order を持つ行
      if (currentMax.order < target.order && line.order < target.order) {
        if (currentMax.order < line.order) {
          return line
        } else {
          return currentMax
        }
      }
      if (currentMax.order > target.order && line.order > target.order) {
        return line
      }
      if (currentMax.order === line.order) {
        return line
      }
      if (currentMax.order < line.order) {
        return currentMax
      }
      return line
    })
  }

  findBelowLine(lines, target) {
    return lines.reduce((currentMin, line) => {
      // target よりも order が大きく、かつ最小の order を持つ行
      if (currentMin.order > target.order && line.order > target.order) {
        if (currentMin.order > line.order) {
          return line
        } else {
          return currentMin
        }
      }
      if (currentMin.order < target.order && line.order < target.order) {
        return line
      }
      if (currentMin.order === line.order) {
        return line
      }
      if (currentMin.order > line.order) {
        return currentMin
      }
      return line
    })
  }

  changeLineOrder(lines, target, direction) {
    let theOther
    if (direction === 'up') {
      theOther = this.findAboveLine(lines, target)
    } else if (direction === 'down') {
      theOther = this.findBelowLine(lines, target)
    } else {
      throw new Error('unsupported direction')
    }

    if (theOther === target) {
      // 交換不可: 対象が見つからない
      console.log('cannot change line order')
      return
    }

    // order の入れ替え
    const currentTargetOrder = target.order
    target.order = theOther.order
    theOther.order = currentTargetOrder

    lines.sort((a, b) => {
      return a.order - b.order
    })
  }

  handleLineUpButtonClick(id) {
    const linesCopy = this.state.lines.slice()
    const target = linesCopy.filter(line => { return line.id === id })
    if (target.length != 1) {
      return
    }
    if (target[0].order <= 0) {
      return
    }

    this.changeLineOrder(linesCopy, target[0], 'up')
    this.setState((state) => ({
      lines: linesCopy,
      reportText: this.buildReportText(state.questname, state.runcount, linesCopy, state.image_url),
      canTweet: false,
    }))
  }

  handleLineDownButtonClick(id) {
    const linesCopy = this.state.lines.slice()
    const target = linesCopy.filter(line => { return line.id === id })
    if (target.length != 1) {
      return
    }
    const maxOrder = linesCopy.reduce((a, b) => { return a > b ? a.order : b.order })
    if (target[0].order >= maxOrder) {
      return
    }

    this.changeLineOrder(linesCopy, target[0], 'down')
    this.setState((state) => ({
      lines: linesCopy,
      reportText: this.buildReportText(state.questname, state.runcount, linesCopy, state.image_url),
      canTweet: false,
    }))
  }

  handleAddRowButtonClick() {
    const lines = this.state.lines
    const newline = {
      id: Math.max(...lines.map(line => { return line.id })) + 1,
      order: Math.max(...lines.map(line => { return line.order })) + 1,
      material: "素材",
      initial: 0,
      add: 0,
      reduce: 0,
      report: 0,
    }
    lines.push(newline)
    this.setState((state) => ({
      lines: lines,
      reportText: this.buildReportText(state.questname, state.runcount, lines, state.image_url),
      canTweet: false,
    }))
  }

  buildReportText(questname, runcount, lines, image_url) {
    const reportText = lines
        .map(line => { return line.material + line.report })
        .join("-")
        .replace(/-\!/g, '\n')

    let value = `【${questname}】${runcount}周
${reportText}
#FGO周回カウンタ https://aoshirobo.net/fatego/rc/
${image_url}`

    const cutIfStartsWith = (expr, key) => {
      if (expr.startsWith(key)) {
        return expr.substring(key.length)
      }
      return expr
    }

    const addedMaterials = lines
        .filter(line => { return line.add != 0})
        .map(line => { return cutIfStartsWith(line.material, '!') + line.add })
        .join('-')
    const reducedMaterials = lines
        .filter((line) => { return line.reduce != 0})
        .map(line => { return cutIfStartsWith(line.material, '!') + line.reduce })
        .join('-')

    const additionalLines = []
    if (addedMaterials.length > 0) {
      additionalLines.push('周回外消費分の加算: ' + addedMaterials)
    }
    if (reducedMaterials.length > 0) {
      additionalLines.push('周回外獲得分の減算: ' + reducedMaterials)
    }
    if (additionalLines.length > 0) {
      value += '\n\n' + additionalLines.join('\n')
    }
    return value + '\n'
  }

  handleShowTweetButton(event) {
    this.setState({ canTweet: true })
  }

  render() {
    let tableComponent
    if (this.state.editMode) {
      tableComponent = (
        <React.Fragment>
          <button className="button is-small is-success" onClick={this.handleCloseClick}>閉じる</button>
          <span className="tag is-info is-light" style={{marginLeft: 0.6 + 'rem'}}>スマホの場合は横向きを強く推奨</span>
          <Table {...this.state}
              onMaterialChange={this.handleMaterialChange}
              onMaterialAddCountChange={this.handleMaterialAddCountChange}
              onMaterialReduceCountChange={this.handleMaterialReduceCountChange}
              onMaterialReportCountChange={this.handleMaterialReportCountChange}
              onLineDeleteButtonClick={this.handleLineDeleteButtonClick}
              onLineUpButtonClick={this.handleLineUpButtonClick}
              onLineDownButtonClick={this.handleLineDownButtonClick}
              onAddRowButtonClick={this.handleAddRowButtonClick}
          />
        </React.Fragment>
      )
    } else {
      tableComponent = (
        <React.Fragment>
          <button className="button is-small is-success" onClick={this.handleEditClick}>報告素材を編集</button>
          <span className="tag is-info is-light" style={{marginLeft: 0.6 + 'rem'}}>スマホの場合は横向きを強く推奨</span>
        </React.Fragment>
      )
    }
    return (
      <div>
        <ReportViewer {...this.state} />
        <QuestNameEditor questname={this.state.questname}
          onQuestNameChange={this.handleQuestNameChange} />
        <RunCountEditor runcount={this.state.runcount}
          onRunCountChange={this.handleRunCountChange} />
        <div style={{marginTop: 1 + 'rem'}}>
          {tableComponent}
        </div>
        <TweetButton {...this.state}
          onShowTweetButton={this.handleShowTweetButton} />
      </div>
    )
  }
}

// 初期値の questname, runcount, data は html 側で定義されている前提
const root = <EditBox questname={questname} runcount={runcount} lines={data} image_url={image_url} />

ReactDOM.render(root, document.getElementById('app0'))
