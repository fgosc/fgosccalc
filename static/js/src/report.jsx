"use strict";
// ver 20200726-01

class TableLine extends React.Component {
  constructor(props) {
    super(props)

    this.handleMaterialChange = this.handleMaterialChange.bind(this)
    this.handleAddChange = this.handleAddChange.bind(this)
    this.handleReduceChange = this.handleReduceChange.bind(this)
    this.handleReportChange = this.handleReportChange.bind(this)
    this.handleEditClick = this.handleEditClick.bind(this)
    this.handleDeleteClick = this.handleDeleteClick.bind(this)
    this.handleUpClick = this.handleUpClick.bind(this)
    this.handleDownClick = this.handleDownClick.bind(this)

    this.state = {
      editResult: false,
      invalidResultValue: false,
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
    const v = event.target.value
    if (v !== "NaN" && isNaN(parseInt(v))) {
      this.setState({ invalidResultValue: true })
    } else {
      this.setState({ invalidResultValue: false })
    }
    this.props.onMaterialReportCountChange(this.props.id, v)
  }

  handleEditClick(event) {
    this.setState({ editResult: true })
    // 直接編集開始時は今までの増減操作をなかったことにする
    this.props.onMaterialAddCountChange(this.props.id, 0)
    this.props.onMaterialReduceCountChange(this.props.id, 0)
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

  render() {
    let addComponent, reduceComponent, reportComponent, editButton

    if (this.state.editResult) {
      addComponent = <span>{this.props.add}</span>
      reduceComponent = <span>{this.props.reduce}</span>
      if (this.state.invalidResultValue) {
        reportComponent = (
          <React.Fragment>
            <input type="text" className="input is-small is-danger" value={this.props.report} onChange={this.handleReportChange} />
            <p className="help is-danger">整数か NaN を入力してください。</p>
          </React.Fragment>
        )
      } else {
        reportComponent = <input type="text" className="input is-small" value={this.props.report} onChange={this.handleReportChange} />
      }
      editButton = ''
    } else {
      addComponent = <input type="number" className="input is-small" min="0" value={this.props.add} onChange={this.handleAddChange} />
      reduceComponent = <input type="number" className="input is-small" min="0" value={this.props.reduce} onChange={this.handleReduceChange} />
      reportComponent = <span>{this.props.report}</span>
      editButton = <button className="button is-small is-success" onClick={this.handleEditClick}>編集</button>
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
          <input type="text" className="input is-small" value={this.props.material} onChange={this.handleMaterialChange} />
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
              <th>増</th>
              <th>減</th>
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
        <ul>
          <li><small><b>増</b> ... 指定数分だけ報告数を増やします。たとえば、周回カウント中に育成等で素材を消費した場合など。</small></li>
          <li><small><b>減</b> ... 指定数分だけ報告数を減らします。たとえば、周回以外で入手した素材を集計から除外したいなど。</small></li>
          <li><small><b>編集</b> ... 解析結果を無視して報告数を直接指定します。解析結果が正しくない場合や、解析ではカウント不可能なアイテム（礼装や種火など）の報告に使います。</small></li>
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

  render() {
    return (
      <div className="field">
        <label className="label">周回場所</label>
        <div className="control">
          <input type="text" className="input is-small" value={this.props.questname} onChange={this.handleChange} />
        </div>
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
    let v = parseInt(this.props.runcount) + delta
    if (v < 0) {
      v = 0
    }
    this.props.onRunCountChange(v)
  }

  handleClick(event) {
    this.addValue(parseInt(event.target.textContent))
  }

  render() {
    return (
      <div>
        <div className="field">
          <label className="label">周回数</label>
          <div className="control">
            <input type="number" className="input is-small" min="0" value={this.props.runcount} onChange={this.handleChange} />
          </div>
        </div>
        <div className="field is-grouped">
          <div className="control">
            <button className="button is-small is-danger" onClick={this.handleClick}>-100</button>
          </div>
          <div className="control">
            <button className="button is-small is-danger" onClick={this.handleClick}>-10</button>
          </div>
          <div className="control">
            <button className="button is-small is-danger" onClick={this.handleClick}>-1</button>
          </div>
          <div className="control">
            <button className="button is-small is-link" onClick={this.handleClick}>+1</button>
          </div>
          <div className="control">
            <button className="button is-small is-link" onClick={this.handleClick}>+10</button>
          </div>
          <div className="control">
            <button className="button is-small is-link" onClick={this.handleClick}>+100</button>
          </div>
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
        <label className="label">周回報告テキスト（編集不可）</label>
        <div className="control">
          <textarea className="textarea is-small" readOnly value={this.props.reportText} rows={numRows} />
        </div>
      </div>
    )
  }
}

class TweetButton extends React.Component {
  isValidCondition(questname, runcount) {
    // questname
    if (questname === '(クエスト名)') {
      return false
    }
    if (questname.length === 0) {
      return false
    }
    const pos = questname.replace(/　/g, ' ').trim().indexOf(' ')
    if (pos < 0) {
      return false
    }
    // runcount
    if (runcount <= 0) {
      return false
    }
    return true
  }

  createTweetButton() {
    const el = document.getElementById('tweet-button')
    if (el === null) {
      return ''
    }
    
    // 周回場所、周回数未設定の場合はボタン非表示
    if (!this.isValidCondition(this.props.questname, this.props.runcount)) {
      return (
        <article className="message is-warning is-small">
          <div className="message-body">周回場所、周回数を設定するとツイートボタンが表示されます。</div>
        </article>
      )
    }

    window.twttr.ready(() => {
      for (let node of el.childNodes) {
        el.removeChild(node)
      }
      window.twttr.widgets.createShareButton(
        '',
        el,
        {
          text: this.props.reportText,
          size: 'large',
        }
      )
    })
    return ''
  }

  componentDidMount() {
    // このタイミングで強制的に一度 render する
    this.setState({})
  }

  render() {
    const node = this.createTweetButton()
    return (
      <div id="tweet-button" style={{ marginTop: 1 + 'rem'}}>{node}</div>
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

    const questname = props.questname
    const runcount = parseInt(props.runcount)
    const lines = props.lines
    this.state = {
      editMode: false,
      questname: questname,
      runcount: runcount,
      lines: lines,
      reportText: this.buildReportText(questname, runcount, lines)
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
        reportText: this.buildReportText(questname, state.runcount, state.lines)
    }))
  }

  handleRunCountChange(runcount) {
    this.setState((state) => ({
      runcount: runcount,
      reportText: this.buildReportText(state.questname, runcount, state.lines)
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
      reportText: this.buildReportText(state.questname, state.runcount, newlines)
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
      reportText: this.buildReportText(state.questname, state.runcount, newlines)
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
      reportText: this.buildReportText(state.questname, state.runcount, newlines)
    }))
  }

  handleMaterialReportCountChange(id, count) {
    const hook = (line) => {
      line.report = count
    }
    const newlines = this.rebuildLines(this.state.lines, hook, id)
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines)
    }))
  }

  handleLineDeleteButtonClick(id) {
    const newlines = this.state.lines.filter(line => { return line.id !== id })
    this.setState((state) => ({
      lines: newlines,
      reportText: this.buildReportText(state.questname, state.runcount, newlines)
    }))
  }

  changeLineOrder(lines, target, direction) {
    if (direction === 'up') {
      target.order -= 1
    } else if (direction == 'down') {
      target.order += 1
    } else {
      throw new Error('unsupported direction')
    }

    const theOthers = lines.filter(line => { return line.id !== target.id && line.order === target.order })
    if (theOthers.length != 1) {
      throw new Error('ambigious lines')
    }
    const theOther = theOthers[0]
    if (direction === 'up') {
      theOther.order += 1
    } else {
      theOther.order -= 1
    }

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
      reportText: this.buildReportText(state.questname, state.runcount, lines)
    }))
  }

  handleLineDownButtonClick(id) {
    const linesCopy = this.state.lines.slice()
    const target = linesCopy.filter(line => { return line.id === id })
    if (target.length != 1) {
      return
    }
    if (target[0].order >= linesCopy.length - 1) {
      return
    }

    this.changeLineOrder(linesCopy, target[0], 'down')
    this.setState((state) => ({
      lines: linesCopy,
      reportText: this.buildReportText(state.questname, state.runcount, lines)
    }))
  }

  handleAddRowButtonClick() {
    const lines = this.state.lines
    const newline = {
      id: lines.length,
      order: lines.length,
      material: "素材",
      initial: 0,
      add: 0,
      reduce: 0,
      report: 0,
    }
    lines.push(newline)
    this.setState((state) => ({
      lines: lines,
      reportText: this.buildReportText(state.questname, state.runcount, lines)
    }))
  }

  buildReportText(questname, runcount, lines) {
    const reportText = lines
        .map(line => { return line.material + line.report })
        .join("-")
        .replace(/-\!/g, '\n')

    let value = `【${questname}】${runcount}周
${reportText}
#FGO周回カウンタ https://aoshirobo.net/fatego/rc/`

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
    return value
  }

  render() {
    let tableComponent
    if (this.state.editMode) {
      tableComponent = (
        <React.Fragment>
          <button className="button is-small is-success" onClick={this.handleCloseClick}>閉じる</button>
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
          <span className="tag is-info is-light" style={{marginLeft: 0.6 + 'rem'}}>スマホの場合は横向きを推奨</span>
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
        <TweetButton {...this.state} />
      </div>
    )
  }
}

// 初期値の questname, runcount, data は html 側で定義されている前提
const root = <EditBox questname={questname} runcount={runcount} lines={data} />

ReactDOM.render(root, document.getElementById('app0'))
