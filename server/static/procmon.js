async function getData(pid) {
    const resp = await fetch(`/proclog/${pid}`)
    if (resp.status === 404) return null
    return await resp.json()
}

window.addEventListener("load", async () => {
    const pid = new URLSearchParams(document.location.search).get("pid")

    const state = document.getElementById("state")
    const output = document.getElementById("output")

    function noPid() {
        state.dataset.state = "failure"
        state.innerHTML = "no PID"
    }
    function invalid() {
        state.dataset.state = "failure"
        state.innerHTML = "invalid or unrecognized PID"
    }

    if (pid == null) {
        noPid()
        return
    }

    const first = await getData(pid)
    if (first == null) {
        invalid()
        return
    }

    const started = Date.now()

    async function iterate() {
        const data = await getData(pid)
        if (data == null) {
            invalid()
            return
        }

        const exitcode = data.exitcode
        const out = data.stdout

        if (exitcode === false) {
            state.dataset.state = "running"
            state.innerHTML = "Running..."
            setTimeout(iterate, 100)
        } else {
            if (exitcode === 0) {
                state.dataset.state = "success"
            } else {
                state.dataset.state = "failure"
            }
            state.innerHTML = `Completed with exit code ${exitcode}`
        }
        const isEmpty = out.length === 0
        if (isEmpty) {
            const duration = Date.now() - started
            output.classList.add("-no-output")
            if (exitcode === false)
                output.innerText = `No output yet... ${Math.round(duration / 100) / 10}s`
            else
                output.innerText = `Command produced no output`
        } else {
            output.classList.remove("-no-output")
            output.innerText = out
        }
    }
    await iterate()
})