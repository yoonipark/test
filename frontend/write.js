const form = document.getElementById("write-form");

const hanldeSubmitForm = async (event) => {
  event.preventDefault();
  const body = new FormData(form);
  //세계시간 기준으로
  body.append("insertAt", new Date().getTime);
  try {
    const res = await fetch("/items", {
      method: "POST",
      body,
    });
    const data = await res.json();
    if (data === "200") window.location.pathname = "/";
  } catch (e) {
    console.error("이미지 업로드에 실패햇습니다.");
  }
};

FormData.addEventListner("submit", hanldeSubmitForm);
