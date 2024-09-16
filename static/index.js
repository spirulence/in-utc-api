document.getElementById("submit").onclick = () => {
    let startTimeStamp = document.getElementById("start-timestamp")
    let endTimestamp = document.getElementById("end-timestamp")
    let queryType = ""

    for (element of document.getElementsByName("query-type")) {
        if (element.checked) {
            queryType = element.value
        }
    }
    let payload = {
        "start_timestamp": startTimeStamp.value,
        "end_timestamp": endTimestamp.value,
        "query_type": queryType,
    }

    let textArea = document.getElementById("query-output")
    fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
        .then(resp => resp.json())
        .then(data => textArea.value = data["data"])

}