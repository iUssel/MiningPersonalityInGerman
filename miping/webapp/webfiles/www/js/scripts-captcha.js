// custom fetch function to implement timeout
function fetchTimeout(url, options, timeout = 100000) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) =>
            setTimeout(() => reject(new Error('timeout')), timeout)
        )
    ]);
}

var userAgreed = false;
// user agreed to terms
function agreeButton() {
    if (userAgreed === false) {
        // reset result display div
        document.querySelectorAll('#send_button').forEach(function(item) {
        item.style.visibility = "visible";
        });

        document.querySelectorAll('#agree_button').forEach(function(item) {
        item.style.backgroundColor = "green";
        item.style.border = "";
        });

        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "https://www.google.com/recaptcha/api.js"; 
        document.getElementsByTagName("head")[0].appendChild(script);
        
        userAgreed = true;
    }
    return true;
};

// submit form to API
document.querySelector('#my_captcha_form').addEventListener("submit",function(evt)
  {
  if (userAgreed){
      // only if user agreed continue
      // reset result display div
      document.querySelectorAll('.result').forEach(function(item) {
        item.style.visibility = "hidden";
      });

      var response = grecaptcha.getResponse();
      if(response.length == 0) 
      { 
        //reCaptcha not verified
        alert("Please verify you are human."); 
        evt.preventDefault();
        return false;
      }
      evt.preventDefault();
      //make loading animation visible
      var loadingAnimation = document.getElementById("loading");
      loadingAnimation.style.visibility = "visible";
      //captcha verified
      handleClick(response) //call API
  } else {
        // user did not agree, hightlight agree button
        document.querySelectorAll('#agree_button').forEach(function(item) {
        item.style.border = "solid red 1px";
        });
  }
});

function showResult(jsonResponse) {
    personalities = jsonResponse;
    // big 5 values are
    var big5List = [
        "big5_openness",
        "big5_conscientiousness",
        "big5_extraversion",
        "big5_agreeableness",
        "big5_neuroticism"
    ];
    // get coverage (percentage of used words)
    coverage = personalities['coverage'];
    // convert to percentage for display (round to 1 decimal point)
    coverage = Math.round(coverage * 1000) / 10 + "%";
    // loop over items and assign values
    big5List.forEach(function (item, index) {
      var big5html = document.getElementById(item);
      var big5value = personalities[item];
      // round to 1 decimal point
      big5html.textContent = Math.round(big5value * 1000) / 10 + "%";
      // set percentage bar accordingly
      big5html.style.width = (big5value * 100) + "%";
    });
    
    var resultHeader = document.getElementById("resultHeader");
    var userName = personalities['userName'];
    resultHeader.innerHTML = "<h6>Your Personality for <a href='https://twitter.com/" + userName + "'>@" + userName + "</a>. Word coverage: " + coverage + ".</h6>";

    //make loading animation hidden
    var loadingAnimation = document.getElementById("loading");
    loadingAnimation.style.visibility = "hidden";

    // make div visible
    document.querySelectorAll('.result').forEach(function(item) {
        item.style.visibility = "visible";
    });
}

function showError(message) {
    //make loading animation hidden
    var loadingAnimation = document.getElementById("loading");
    loadingAnimation.style.visibility = "hidden";
    // reset result display div
    document.querySelectorAll('.result').forEach(function(item) {
    item.style.visibility = "hidden";
    });
    console.log(message)
    alert(message);
}

function statusCheck(response) {
  if (response.ok) {
    return 1;
  } else {
    if (response.status == 502 || response.status == 404 ) {
        // backend unreachable
        showError("Backend unreachable. Please try again later.")
    } else if (response.status == 400){
        // these are invalid user inputs and will be handled outside of this function
        return 400;
    }
    return false;
  }
}

async function handleClick(token) {
        var twitterHandle = document.getElementById('twitterHandleInput').value;
        var data = {
            twitterHandle: twitterHandle,
            token: token
        };

        const res = await fetchTimeout('/api/personality', {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: 'post',
            body: JSON.stringify(data)
        }, 60000) // timeout nach 60 sekunden
        .catch((e) => {
            // handle errors and timeout error
            showError("Timeout after 60 seconds");
        })
        // check status
        var continueVal = statusCheck(res);
        if (continueVal == 1){
            // wait for body to be fully loaded, as json
            const body = await res.json();
            // check was successful
            showResult(body);
        } else if (continueVal == 400) {
            // error in user input
            // details are json encoded by backend
            // wait for body to be fully loaded, as json
            const body = await res.json();
            // show error
            showError(body["message"]);
        }

}