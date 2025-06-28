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

    async function iterate() {
        const data = await getData(pid)

        const exitcode = data.exitcode

        if (!exitcode) {
            state.dataset.state = "running"
            state.innerHTML = "Running..."
        } else {
            if (exitcode === 0) {
                state.dataset.state = "success"
            } else {
                state.dataset.state = "failure"
            }
            state.innerHTML = `Completed with exit code ${exitcode}`
        }

        setTimeout(iterate, 250)
    }
    await iterate()
})