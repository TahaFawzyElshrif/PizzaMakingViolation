const listSection = document.getElementById("list_section");

// Initial structure
let itemsData = [
    {
        title: "Violations",
        elements: []
    }
];

// Function to render list dynamically
function renderList(itemsData) {
    listSection.innerHTML = ""; // clear old items

    itemsData.forEach(item => {
        console.log(item)
        const listItem = document.createElement("div");
        listItem.className = "list-item";

        // Add title
        const itemTitle = document.createElement("h2");
        itemTitle.className = "item-title";
        itemTitle.textContent = item.title;
        listItem.appendChild(itemTitle);

        const elementsContainer = document.createElement("div");
        elementsContainer.className = "item-elements";

        // Loop over elements
        item.elements.forEach(el => {
            const elementDiv = document.createElement("div");
            elementDiv.className = "element";

            // Text
            const elTitle = document.createElement("p");
            elTitle.className = "element-title";
            elTitle.textContent = el.name;
            elementDiv.appendChild(elTitle);

            // Image (handle empty or invalid src)
            const elImg = document.createElement("img");
            elImg.src = el.img || "images/placeholder.jpg"; // fallback if empty
            elImg.alt = el.name || "Violation Image";
            elementDiv.appendChild(elImg);

            elementsContainer.appendChild(elementDiv);
        });

        listItem.appendChild(elementsContainer);
        listSection.appendChild(listItem);
    });
}

// Initial render
renderList(itemsData);

// Periodically fetch data from backend every 5 seconds
setInterval(async () => {
    try {
        const response = await fetch("http://localhost:8001/api/items"); // backend API
        if (!response.ok) throw new Error("Failed to fetch data");
        const data = await response.json();

        // Wrap elements under a single title
        const formattedData = [
            {
                title: "Violations",
                elements: data.flatMap(item => item.elements || [])
            }
        ];

        renderList(formattedData);
    } catch (err) {
        console.error("Error fetching data:", err);
    }
}, 5000);
