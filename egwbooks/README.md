# Full Recap of My EGW Books Project

## Introduction

This project showcases a comprehensive approach to building an end to end "Full Stack Data Science" aplication. I successfully integrated web scraping, database management, web development, Docker, data analysis, machine learning, business insights and ETL processes into a single complex project.

The notebooks further demonstrate my ability to extract actionable insights from data and develop predictive models to guide business decisions. This project not only highlights my technical skills but also my ability to solve real-world problems using a combination of technologies.

- Technologies Used:

Web Development: Flask, HTML/CSS, JavaScript

Containerization: Docker, Docker Compose

Database: SQLite, SQLAlchemy

Data Analysis: Pandas, Matplotlib, Seaborn, Jupyter Notebook

Data Science: Scikit-Learn, Statsmodels

Machine Learning: Linear Regression, Decision Tree, Random Forest, Gradient Boosting, SVR, Cosine Similarity.

ETL/Data Pipeline: Apache Airflow

Cloud Integration: AWS S3, Boto3

Additional Libraries: BeautifulSoup, Requests, KMeans.

## 1. Web Scraping and Data Collection

I started the project by scraping data from [egw official website](https://m.egwwritings.org/es) to gather information about Ellen G. White (EGW) books. I used Python’s BeautifulSoup and Requests libraries to extract data such as book titles, descriptions, prices, and more.

### Technologies: Python, BeautifulSoup, Requests

## 2. Web Application Development

I developed an online bookstore for EGW books using Flask, a lightweight web framework. The application allows users to browse, search, and purchase books. Here's a breakdown of the development process:

- Database Integration: I connected the app to multiple SQLite databases (egw.db, users.db, orders.db, feedback.db) to store data on books, users, orders, and feedback.

- User Authentication: Implemented user registration and login functionalities. Users can create accounts, log in, and view their order history, making the app more personalized and user-friendly.

- Top 10 Books Functionality: I added a function to display the top 10 best-selling books on the homepage, providing users with easy access to popular books, thanks to database integration and SQL querys.

Code Structuring: The app.py file is well-structured with clear comments, making the codebase easy to understand and maintain.

### Technologies: Flask, HTML/CSS, SQLite, SQLAlchemy

## 3. Docker Compose

I created a docker-compose.yaml file to manage multi-container applications, including the web server, database, and Airflow.

### Technologies: Docker, Docker Compose

## 4. SQL Database Design and Management

I designed and managed multiple SQLite databases to store and manage data efficiently. Here’s what I did:

- Database Design: I created tables for books, users, orders, and feedback, ensuring they are well-structured and optimized for performance.

- Complex Queries: I wrote complex SQL queries to extract valuable insights, such as identifying the top buyers, most popular books, and revenue generated.

### Technologies: SQLite, SQLAlchemy, SQL

## 5. ETL and Data Pipeline (Airflow DAG)

I implemented an ETL pipeline using Apache Airflow to automate the extraction, transformation, and loading (ETL) of data to an Amazon S3 bucket:

- Data Extraction and Transformation: The pipeline pulls data from the SQLite databases, transforms it into a suitable format, and saves it as CSV files. This ensures the data is always ready for analysis and reporting.

- Task Automation: The pipeline is scheduled to run daily, making sure the data is up-to-date without manual intervention. This was crucial for maintaining the integrity and timeliness of the data.

### Technologies: Apache Airflow, SQLite, Python

## 6. AWS S3 Integration

I uploaded the extracted data to an AWS S3 bucket for cloud storage. For this purpose, I used an AWS Identity and Access Management (IAM) user with the necessary permissions to access S3.

### Technologies: AWS S3, IAM, Python, Boto3

## 7. Data Analysis (Jupyter Notebook)

I conducted an in-depth exploratory data analysis (EDA) to extract insights from the sales data. Here’s what I did:

- Average Money Spent per Order: I calculated the average money spent per order and visualized the distribution using histograms and boxplots. This helped me understand customer spending behavior.

- Top Buyers and Books: I identified the top buyers and the most purchased books, which provided insights into customer preferences and potential target audiences for marketing campaigns.

- Peak Purchase Times: By analyzing the days and hours when most purchases were made, I determined that Sundays at 12 PM were the peak times for sales. This information was crucial for timing promotions effectively.

- Cluster Analysis: I performed a cluster analysis to group similar orders based on the day and hour of purchase. This helped in identifying patterns in customer behavior, which could be leveraged for personalized marketing strategies.

- Conclusion: The EDA revealed that "The Desire of Ages" was the top-selling book, and Sundays at 12 PM were the best times for marketing efforts. I recommended launching a targeted marketing campaign with a budget of less than $299 to maximize returns.

### Technologies: Jupyter Notebook, Pandas, Matplotlib, Seaborn, KMeans (for clustering)

## 8. Data Science and Machine Learning (Jupyter Notebook)

To further enhance the insights, I delved into data science and machine learning. Here’s how:

- Feature Engineering: I created a synthetic dataset based on real-world data from Facebook Ads, including variables like budgets, cost per impression, cost per click, conversion rates, impressions, clicks, sales, and revenue. This dataset was crucial for training machine learning models.

- Model Development: I developed and trained five different models to predict revenue from marketing campaigns:

Linear Regression

Decision Tree Regressor

Random Forest Regressor

Gradient Boosting Regressor

Support Vector Regressor

- Model Evaluation: After evaluating all models, the Linear Regression model provided the most accurate predictions. The model predicted that an investment of $299 would generate a revenue of $194.58, indicating a potential loss.

- Hypothesis Testing: I conducted a T-Test, which rejected the null hypothesis, suggesting that the predicted revenue is significantly less than the budget. Based on these findings, I recommended not proceeding with the marketing campaign due to the expected financial loss.

### Technologies: Jupyter Notebook, Pandas, Scikit-Learn, Statsmodels

