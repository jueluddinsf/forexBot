# Selenium WebDriver with Java: A Comprehensive Guide

## Table of Contents
1. [Introduction to Selenium WebDriver](#introduction-to-selenium-webdriver)
2. [Setting Up the Environment](#setting-up-the-environment)
3. [Selenium WebDriver Basics](#selenium-webdriver-basics)
4. [Writing Your First Selenium Test](#writing-your-first-selenium-test)
5. [Locators in Selenium](#locators-in-selenium)
6. [Handling Web Elements](#handling-web-elements)
7. [Synchronization in Selenium](#synchronization-in-selenium)
8. [Advanced Selenium Concepts](#advanced-selenium-concepts)
9. [Introduction to Cucumber](#introduction-to-cucumber)
10. [Setting Up Cucumber with Selenium](#setting-up-cucumber-with-selenium)
11. [Integrating Cucumber with Selenium](#integrating-cucumber-with-selenium)
12. [Page Object Model (POM)](#page-object-model-pom)
13. [TestNG Integration with Selenium](#testng-integration-with-selenium)
14. [Continuous Integration with Jenkins](#continuous-integration-with-jenkins)
15. [Best Practices for Selenium Automation](#best-practices-for-selenium-automation)
16. [Common Challenges and Solutions](#common-challenges-and-solutions)
17. [Real-World Examples and Use Cases](#real-world-examples-and-use-cases)
18. [Extending Selenium with Third-Party Tools](#extending-selenium-with-third-party-tools)
19. [Troubleshooting and Debugging](#troubleshooting-and-debugging)
20. [Conclusion and Next Steps](#conclusion-and-next-steps)

## Introduction to Selenium WebDriver

### What is Selenium WebDriver?
Selenium WebDriver is a powerful open-source automation framework for web applications. It provides:
- Support for multiple programming languages (Java, Python, C#, etc.)
- Cross-browser compatibility
- Native browser automation capabilities
- Rich API for web element interactions

### Key Features
- Browser automation
- Cross-platform support
- Multiple programming language bindings
- Integration with testing frameworks
- Support for parallel test execution

### Additional Features
1. **Cross-Browser Testing**
   - Parallel execution across browsers
   - Browser-specific capabilities
   - Remote WebDriver support
   - Cloud testing integration

2. **Mobile Testing Support**
   - Appium integration
   - Mobile web testing
   - Responsive design testing
   - Touch actions support

3. **Advanced Automation Features**
   - Screenshot capture
   - Network traffic monitoring
   - Performance metrics collection
   - Cookie and session management

### WebDriver Setup for Different Browsers

#### 1. Chrome Setup
```java
// Using WebDriverManager (Recommended)
WebDriverManager.chromedriver().setup();
ChromeOptions options = new ChromeOptions();
options.addArguments("--start-maximized");
options.addArguments("--disable-notifications");
WebDriver driver = new ChromeDriver(options);

// Manual Setup
System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
WebDriver driver = new ChromeDriver();
```

#### 2. Firefox Setup
```java
// Using WebDriverManager
WebDriverManager.firefoxdriver().setup();
FirefoxOptions options = new FirefoxOptions();
options.addArguments("-private");
WebDriver driver = new FirefoxDriver(options);
```

#### 3. Edge Setup
```java
WebDriverManager.edgedriver().setup();
EdgeOptions options = new EdgeOptions();
options.addArguments("--inprivate");
WebDriver driver = new EdgeDriver(options);
```

### Browser Options and Capabilities

#### Chrome Options
```java
ChromeOptions options = new ChromeOptions();
// Headless mode
options.addArguments("--headless");
// Disable GPU
options.addArguments("--disable-gpu");
// Incognito mode
options.addArguments("--incognito");
// Disable extensions
options.addArguments("--disable-extensions");
// Set download directory
HashMap<String, Object> prefs = new HashMap<>();
prefs.put("download.default_directory", "/path/to/download");
options.setExperimentalOption("prefs", prefs);
```

#### Firefox Options
```java
FirefoxOptions options = new FirefoxOptions();
// Headless mode
options.setHeadless(true);
// Set binary location
options.setBinary("/path/to/firefox");
// Set preferences
options.addPreference("browser.download.folderList", 2);
options.addPreference("browser.download.dir", "/path/to/download");
```

## Selenium WebDriver Basics

### WebDriver Architecture
```plaintext
                    ┌─────────────────┐
                    │  Test Script    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Selenium WebDriver│
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐         ┌────────▼────────┐
    │  Browser Drivers   │         │  Browser        │
    │  - ChromeDriver   │         │  - Chrome       │
    │  - GeckoDriver    │◄────────►  - Firefox      │
    │  - EdgeDriver     │         │  - Edge         │
    └───────────────────┘         └─────────────────┘
```

### Supported Browsers and Drivers
| Browser | Driver | Download Link |
|---------|--------|--------------|
| Chrome | ChromeDriver | [Download](https://sites.google.com/chromium.org/driver/) |
| Firefox | GeckoDriver | [Download](https://github.com/mozilla/geckodriver/releases) |
| Edge | EdgeDriver | [Download](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) |
| Safari | SafariDriver | Built into macOS |

## Writing Your First Selenium Test

### 1. Creating a Maven Project
1. **Create Project Structure**
   ```bash
   1. Open Eclipse
   2. File > New > Maven Project
   3. Create Simple Project (skip archetype selection)
   4. Group ID: com.example.selenium
   5. Artifact ID: selenium-test-project
   6. Version: 1.0-SNAPSHOT
   ```

2. **Add Dependencies**
   Add to `pom.xml`:
   ```xml
   <dependencies>
       <!-- Selenium WebDriver -->
       <dependency>
           <groupId>org.seleniumhq.selenium</groupId>
           <artifactId>selenium-java</artifactId>
           <version>4.12.0</version>
       </dependency>
       
       <!-- TestNG -->
       <dependency>
           <groupId>org.testng</groupId>
           <artifactId>testng</artifactId>
           <version>7.8.0</version>
           <scope>test</scope>
       </dependency>
   </dependencies>
   ```

### 2. Writing Basic Test
1. **Create Test Class**
   ```java
   import org.openqa.selenium.WebDriver;
   import org.openqa.selenium.chrome.ChromeDriver;
   import org.testng.annotations.Test;
   
   public class FirstSeleniumTest {
       @Test
       public void testGoogleSearch() {
           // Initialize WebDriver
           WebDriver driver = new ChromeDriver();
           
           try {
               // Navigate to website
               driver.get("https://www.google.com");
               
               // Print title
               System.out.println("Page Title: " + driver.getTitle());
               
           } finally {
               // Close browser
               driver.quit();
           }
       }
   }
   ```

2. **Run Test**
   ```bash
   1. Right-click on test class
   2. Run As > TestNG Test
   ```

## Locators in Selenium

### Types of Locators
1. **ID Locator** (Most Preferred)
   ```java
   driver.findElement(By.id("username"));
   ```

2. **Name Locator**
   ```java
   driver.findElement(By.name("user_name"));
   ```

3. **Class Name Locator**
   ```java
   driver.findElement(By.className("login-button"));
   ```

4. **XPath Locator**
   ```java
   // Absolute XPath (not recommended)
   driver.findElement(By.xpath("/html/body/div[1]/input"));
   
   // Relative XPath (preferred)
   driver.findElement(By.xpath("//input[@id='username']"));
   ```

5. **CSS Selector**
   ```java
   // ID selector
   driver.findElement(By.cssSelector("#username"));
   
   // Class selector
   driver.findElement(By.cssSelector(".login-button"));
   ```

6. **Link Text & Partial Link Text**
   ```java
   // Full link text
   driver.findElement(By.linkText("Sign Up"));
   
   // Partial link text
   driver.findElement(By.partialLinkText("Sign"));
   ```

### Best Practices for Locators
1. **Priority Order**
   - ID > Name > CSS Selector > XPath
   - Avoid absolute XPath
   - Use unique and stable attributes

2. **Dynamic Elements**
   ```java
   // Contains text
   By.xpath("//div[contains(text(), 'Welcome')]");
   
   // Starts with
   By.cssSelector("div[id^='dynamic_']");
   ```

## Handling Web Elements

### 1. Text Input Operations
```java
// Type text
WebElement element = driver.findElement(By.id("username"));
element.sendKeys("testuser");

// Clear text
element.clear();

// Get text value
String text = element.getAttribute("value");
```

### 2. Button Operations
```java
// Click button
WebElement button = driver.findElement(By.id("submit"));
button.click();

// Check if enabled
boolean isEnabled = button.isEnabled();

// Check if displayed
boolean isDisplayed = button.isDisplayed();
```

### 3. Dropdown Handling
```java
// Initialize Select object
Select dropdown = new Select(driver.findElement(By.id("country")));

// Select by visible text
dropdown.selectByVisibleText("United States");

// Select by value
dropdown.selectByValue("US");

// Select by index
dropdown.selectByIndex(1);

// Get selected option
String selected = dropdown.getFirstSelectedOption().getText();
```

### 4. Checkbox and Radio Buttons
```java
WebElement checkbox = driver.findElement(By.id("terms"));

// Check if selected
boolean isSelected = checkbox.isSelected();

// Click to toggle
if (!isSelected) {
    checkbox.click();
}
```

### 5. Alert Handling
```java
// Switch to alert
Alert alert = driver.switchTo().alert();

// Accept alert (OK)
alert.accept();

// Dismiss alert (Cancel)
alert.dismiss();

// Get alert text
String alertText = alert.getText();

// Enter text in prompt
alert.sendKeys("Test Input");
```

## Synchronization in Selenium

### 1. Implicit Wait
```java
// Set implicit wait for entire session
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
```

### 2. Explicit Wait
```java
// Create WebDriverWait instance
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

// Wait for element to be visible
WebElement element = wait.until(
    ExpectedConditions.visibilityOfElementLocated(By.id("username"))
);

// Wait for element to be clickable
element = wait.until(
    ExpectedConditions.elementToBeClickable(By.id("submit"))
);
```

### 3. Fluent Wait
```java
// Create FluentWait instance
Wait<WebDriver> wait = new FluentWait<WebDriver>(driver)
    .withTimeout(Duration.ofSeconds(30))
    .pollingEvery(Duration.ofSeconds(5))
    .ignoring(NoSuchElementException.class);

// Wait for element
WebElement element = wait.until(driver -> {
    return driver.findElement(By.id("dynamicElement"));
});
```

## Advanced Selenium Concepts

### 1. Handling Multiple Windows
```java
// Get current window handle
String mainWindow = driver.getWindowHandle();

// Switch to new window
for (String handle : driver.getWindowHandles()) {
    if (!handle.equals(mainWindow)) {
        driver.switchTo().window(handle);
        break;
    }
}

// Switch back to main window
driver.switchTo().window(mainWindow);
```

### 2. Frame Handling
```java
// Switch to frame by index
driver.switchTo().frame(0);

// Switch to frame by name/ID
driver.switchTo().frame("frameName");

// Switch to frame by WebElement
WebElement frameElement = driver.findElement(By.id("frameId"));
driver.switchTo().frame(frameElement);

// Switch back to default content
driver.switchTo().defaultContent();
```

### 3. Actions Class
```java
// Create Actions instance
Actions actions = new Actions(driver);

// Hover over element
actions.moveToElement(element).perform();

// Drag and drop
actions.dragAndDrop(source, target).perform();

// Right click
actions.contextClick(element).perform();

// Double click
actions.doubleClick(element).perform();
```

### 4. Taking Screenshots
```java
// Take screenshot
File screenshot = ((TakesScreenshot) driver)
    .getScreenshotAs(OutputType.FILE);
Files.copy(screenshot.toPath(), 
    Paths.get("screenshot.png"));
```

### 5. JavaScript Execution
```java
JavascriptExecutor js = (JavascriptExecutor) driver;

// Click element
js.executeScript("arguments[0].click();", element);

// Scroll into view
js.executeScript(
    "arguments[0].scrollIntoView(true);", element);

// Scroll to bottom
js.executeScript(
    "window.scrollTo(0, document.body.scrollHeight)");
```

## Introduction to Cucumber

### What is Cucumber?
Cucumber is a Behavior-Driven Development (BDD) tool that allows you to write test scenarios in plain English using Gherkin syntax. This approach bridges the gap between business stakeholders and development teams.

### 1. Gherkin Syntax
```gherkin
Feature: User Authentication
  As a user
  I want to log in to the application
  So that I can access my account

  Scenario: Successful Login
    Given I am on the login page
    When I enter username "testuser" and password "password123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  Scenario Outline: Invalid Login
    Given I am on the login page
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then I should see error message "<message>"

    Examples:
      | username | password | message                 |
      | invalid  | wrong    | Invalid credentials     |
      | testuser |          | Password is required    |
      |          | pass123  | Username is required    |
```

### 2. Project Structure
```plaintext
src
├── test
│   ├── java
│   │   └── com.example.test
│   │       ├── steps
│   │       │   └── LoginSteps.java
│   │       ├── pages
│   │       │   └── LoginPage.java
│   │       └── runners
│   │           └── TestRunner.java
│   └── resources
│       └── features
│           └── login.feature
```

## Setting Up Cucumber with Selenium

### 1. Add Dependencies
Add to `pom.xml`:
```xml
<dependencies>
    <!-- Cucumber Dependencies -->
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-java</artifactId>
        <version>7.14.0</version>
    </dependency>
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-junit</artifactId>
        <version>7.14.0</version>
    </dependency>
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-testng</artifactId>
        <version>7.14.0</version>
    </dependency>
</dependencies>
```

### 2. Create Feature File
Create `src/test/resources/features/login.feature`:
```gherkin
Feature: Login Functionality
  
  Scenario: Successful Login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to dashboard
```

### 3. Implement Step Definitions
Create `src/test/java/steps/LoginSteps.java`:
```java
package steps;

import io.cucumber.java.en.*;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import pages.LoginPage;

public class LoginSteps {
    private WebDriver driver;
    private LoginPage loginPage;

    @Given("I am on the login page")
    public void navigateToLoginPage() {
        driver = new ChromeDriver();
        loginPage = new LoginPage(driver);
        driver.get("https://example.com/login");
    }

    @When("I enter valid credentials")
    public void enterValidCredentials() {
        loginPage.enterUsername("testuser");
        loginPage.enterPassword("password123");
    }

    @And("I click the login button")
    public void clickLoginButton() {
        loginPage.clickLogin();
    }

    @Then("I should be redirected to dashboard")
    public void verifyDashboard() {
        // Add verification logic
    }
}
```

### 4. Create Test Runner
Create `src/test/java/runners/TestRunner.java`:
```java
package runners;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
    features = "src/test/resources/features",
    glue = {"steps"},
    plugin = {
        "pretty",
        "html:target/cucumber-reports/cucumber-pretty",
        "json:target/cucumber-reports/CucumberTestReport.json"
    }
)
public class TestRunner extends AbstractTestNGCucumberTests {
}
```

## Page Object Model (POM)

### 1. Base Page
```java
public class BasePage {
    protected WebDriver driver;
    protected WebDriverWait wait;

    public BasePage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    protected WebElement waitForElement(By locator) {
        return wait.until(ExpectedConditions.presenceOfElementLocated(locator));
    }

    protected void click(By locator) {
        waitForElement(locator).click();
    }

    protected void type(By locator, String text) {
        waitForElement(locator).sendKeys(text);
    }
}
```

### 2. Page Class Example
```java
public class LoginPage extends BasePage {
    // Locators
    private By usernameField = By.id("username");
    private By passwordField = By.id("password");
    private By loginButton = By.id("login");
    private By errorMessage = By.className("error-message");

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    public void enterUsername(String username) {
        type(usernameField, username);
    }

    public void enterPassword(String password) {
        type(passwordField, password);
    }

    public void clickLogin() {
        click(loginButton);
    }

    public String getErrorMessage() {
        return waitForElement(errorMessage).getText();
    }

    public void login(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }
}
```

## TestNG Integration

### 1. Test Configuration
```java
public class BaseTest {
    protected WebDriver driver;
    
    @BeforeMethod
    public void setup() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }
    
    @AfterMethod
    public void teardown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
```

### 2. Test Class Example
```java
public class LoginTest extends BaseTest {
    private LoginPage loginPage;
    
    @BeforeMethod
    public void setupTest() {
        loginPage = new LoginPage(driver);
        driver.get("https://example.com/login");
    }
    
    @Test
    public void testSuccessfulLogin() {
        loginPage.login("testuser", "password123");
        Assert.assertEquals(driver.getTitle(), "Dashboard");
    }
    
    @Test(dataProvider = "invalidLoginData")
    public void testInvalidLogin(String username, String password, String expectedError) {
        loginPage.login(username, password);
        Assert.assertEquals(loginPage.getErrorMessage(), expectedError);
    }
    
    @DataProvider
    public Object[][] invalidLoginData() {
        return new Object[][] {
            {"invalid", "wrong", "Invalid credentials"},
            {"testuser", "", "Password is required"},
            {"", "password123", "Username is required"}
        };
    }
}
```

## Continuous Integration with Jenkins

### 1. Jenkins Pipeline
Create `Jenkinsfile`:
```groovy
pipeline {
    agent any
    
    tools {
        maven 'Maven 3.9.5'
        jdk 'JDK 21'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your/repository.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean compile'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
            post {
                always {
                    junit '**/target/surefire-reports/*.xml'
                    cucumber '**/target/cucumber-reports/*.json'
                }
            }
        }
    }
}
```

### 2. Jenkins Job Configuration
1. Create New Pipeline Job
2. Configure Git Repository
3. Configure Build Triggers
4. Configure Email Notifications
5. Configure Test Reports

## Best Practices

### 1. Code Organization
- Use Page Object Model
- Implement Base classes for common functionality
- Separate test data from test logic
- Use configuration files for environment-specific data

### 2. Test Design
- Write independent tests
- Follow AAA pattern (Arrange, Act, Assert)
- Use meaningful test names
- Implement proper error handling
- Add detailed test descriptions

### 3. Framework Design
- Implement logging
- Create detailed test reports
- Use test categories/groups
- Implement retry logic for flaky tests
- Use proper wait strategies

### 4. Maintenance
- Regular code reviews
- Update dependencies
- Remove/update obsolete tests
- Document framework changes
- Version control test data

## Troubleshooting

### Common Issues and Solutions

1. **Element Not Found**
   ```java
   // Solution 1: Add explicit wait
   WebElement element = new WebDriverWait(driver, Duration.ofSeconds(10))
       .until(ExpectedConditions.presenceOfElementLocated(locator));
   
   // Solution 2: Check iframe
   driver.switchTo().frame("frameName");
   
   // Solution 3: Refresh stale element
   element = driver.findElement(locator);
   ```

2. **Test Stability**
   ```java
   // Implement retry analyzer
   @Test(retryAnalyzer = RetryAnalyzer.class)
   public void flakeyTest() {
       // Test logic
   }
   ```

3. **Browser Compatibility**
   ```java
   // Use WebDriver manager
   WebDriverManager.chromedriver().setup();
   WebDriverManager.firefoxdriver().setup();
   ```

## Resources for Further Learning

### Official Documentation
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [TestNG Documentation](https://testng.org/doc/)
- [Cucumber Documentation](https://cucumber.io/docs/cucumber/)

### Best Practices Guides
- [Selenium Best Practices](https://www.selenium.dev/documentation/guidelines/best_practices/)
- [Page Object Pattern](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)
- [Test Design Patterns](https://www.selenium.dev/documentation/test_practices/encouraged/design_patterns/)

### Community Resources
- [Selenium GitHub](https://github.com/SeleniumHQ/selenium)
- [Stack Overflow - Selenium](https://stackoverflow.com/questions/tagged/selenium)
- [Selenium Blog](https://www.selenium.dev/blog/)

## Advanced Web Element Interactions

### 1. Complex Mouse Actions
```java
Actions actions = new Actions(driver);

// Chain multiple actions
actions
    .moveToElement(menuElement)
    .pause(Duration.ofSeconds(1))
    .click(subMenuElement)
    .build()
    .perform();

// Drag and drop with offset
actions
    .clickAndHold(sourceElement)
    .moveByOffset(100, 200)
    .release()
    .perform();

// Complex keyboard interactions
actions
    .keyDown(Keys.CONTROL)
    .click(element1)
    .click(element2)
    .keyUp(Keys.CONTROL)
    .perform();
```

### 2. Shadow DOM Handling
```java
// Access Shadow DOM elements
SearchContext shadow = element.getShadowRoot();
WebElement shadowElement = shadow.findElement(By.cssSelector(".shadow-content"));

// Custom method for deep shadow DOM
public WebElement findShadowElement(WebElement host, String cssSelector) {
    JavascriptExecutor js = (JavascriptExecutor) driver;
    return (WebElement) js.executeScript(
        "return arguments[0].shadowRoot.querySelector(arguments[1])",
        host, cssSelector
    );
}
```

### 3. File Upload Handling
```java
// Standard file input
WebElement fileInput = driver.findElement(By.cssSelector("input[type='file']"));
fileInput.sendKeys("/path/to/file.jpg");

// Custom file upload dialog
public void uploadFile(String filePath) {
    try {
        StringSelection stringSelection = new StringSelection(filePath);
        Toolkit.getDefaultToolkit().getSystemClipboard()
            .setContents(stringSelection, null);
        
        Robot robot = new Robot();
        robot.keyPress(KeyEvent.VK_CONTROL);
        robot.keyPress(KeyEvent.VK_V);
        robot.keyRelease(KeyEvent.VK_V);
        robot.keyRelease(KeyEvent.VK_CONTROL);
        robot.keyPress(KeyEvent.VK_ENTER);
        robot.keyRelease(KeyEvent.VK_ENTER);
    } catch (AWTException e) {
        e.printStackTrace();
    }
}
```

## Advanced Wait Strategies

### 1. Custom Wait Conditions
```java
// Custom expected condition
public class ElementContainsText implements ExpectedCondition<Boolean> {
    private By locator;
    private String text;

    public ElementContainsText(By locator, String text) {
        this.locator = locator;
        this.text = text;
    }

    @Override
    public Boolean apply(WebDriver driver) {
        try {
            String elementText = driver.findElement(locator).getText();
            return elementText.contains(text);
        } catch (StaleElementReferenceException e) {
            return false;
        }
    }
}

// Usage
wait.until(new ElementContainsText(By.id("message"), "Success"));
```

### 2. Dynamic Waits
```java
public class DynamicWait {
    private WebDriver driver;
    private Duration timeout;
    private Duration polling;

    public DynamicWait(WebDriver driver) {
        this.driver = driver;
        this.timeout = Duration.ofSeconds(30);
        this.polling = Duration.ofMillis(500);
    }

    public WebElement waitForElement(By locator) {
        FluentWait<WebDriver> wait = new FluentWait<>(driver)
            .withTimeout(timeout)
            .pollingEvery(polling)
            .ignoring(NoSuchElementException.class)
            .ignoring(StaleElementReferenceException.class);

        return wait.until(driver -> {
            WebElement element = driver.findElement(locator);
            if (element.isDisplayed() && element.isEnabled()) {
                return element;
            }
            return null;
        });
    }
}
```

## Advanced Framework Features

### 1. Retry Mechanism
```java
public class RetryAnalyzer implements IRetryAnalyzer {
    private int count = 0;
    private static final int MAX_RETRY = 3;

    @Override
    public boolean retry(ITestResult result) {
        if (!result.isSuccess()) {
            if (count < MAX_RETRY) {
                count++;
                result.setStatus(ITestResult.FAILURE);
                return true;
            } else {
                result.setStatus(ITestResult.FAILURE);
            }
        } else {
            result.setStatus(ITestResult.SUCCESS);
        }
        return false;
    }
}

// Listener to apply retry to all tests
public class RetryListener implements IAnnotationTransformer {
    @Override
    public void transform(ITestAnnotation annotation, 
                         Class testClass, 
                         Constructor testConstructor, 
                         Method testMethod) {
        annotation.setRetryAnalyzer(RetryAnalyzer.class);
    }
}
```

### 2. Custom Reporting
```java
public class CustomReporter implements IReporter {
    @Override
    public void generateReport(List<XmlSuite> xmlSuites, 
                             List<ISuite> suites, 
                             String outputDirectory) {
        // Create custom report
        try (FileWriter writer = new FileWriter(
                new File(outputDirectory, "custom-report.html"))) {
            // Generate HTML report
            writer.write("<html><body>");
            for (ISuite suite : suites) {
                Map<String, ISuiteResult> results = suite.getResults();
                for (ISuiteResult result : results.values()) {
                    ITestContext context = result.getTestContext();
                    writeTestResults(writer, context);
                }
            }
            writer.write("</body></html>");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void writeTestResults(FileWriter writer, 
                                ITestContext context) 
            throws IOException {
        // Write test results in HTML format
    }
}
```

### 3. Screenshot Management
```java
public class ScreenshotManager {
    private WebDriver driver;
    private String screenshotDir;

    public ScreenshotManager(WebDriver driver) {
        this.driver = driver;
        this.screenshotDir = "test-output/screenshots/";
        new File(screenshotDir).mkdirs();
    }

    public String captureScreen(String filename) {
        String filepath = screenshotDir + filename + ".png";
        try {
            TakesScreenshot ts = (TakesScreenshot) driver;
            File source = ts.getScreenshotAs(OutputType.FILE);
            File destination = new File(filepath);
            FileUtils.copyFile(source, destination);
            return filepath;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    public String captureElementScreen(WebElement element, 
                                     String filename) {
        String filepath = screenshotDir + filename + ".png";
        try {
            File screenshot = element.getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filepath));
            return filepath;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}
```

## Performance Testing Integration

### 1. Browser Performance Metrics
```java
public class PerformanceMetrics {
    private JavascriptExecutor js;

    public PerformanceMetrics(WebDriver driver) {
        this.js = (JavascriptExecutor) driver;
    }

    public Map<String, Object> getNavigationTiming() {
        return (Map<String, Object>) js.executeScript(
            "return window.performance.timing.toJSON();"
        );
    }

    public Object getPageLoadTime() {
        return js.executeScript(
            "return performance.timing.loadEventEnd - " +
            "performance.timing.navigationStart;"
        );
    }

    public List<Map<String, Object>> getNetworkRequests() {
        return (List<Map<String, Object>>) js.executeScript(
            "return window.performance.getEntriesByType('resource');"
        );
    }
}
```

### 2. Network Throttling
```java
public class NetworkConditions {
    public static void setNetworkConditions(ChromeDriver driver, 
                                          String preset) {
        Map<String, Object> conditions = new HashMap<>();
        switch (preset.toLowerCase()) {
            case "3g":
                conditions.put("offline", false);
                conditions.put("latency", 100);
                conditions.put("downloadThroughput", 750 * 1024);
                conditions.put("uploadThroughput", 250 * 1024);
                break;
            case "4g":
                conditions.put("offline", false);
                conditions.put("latency", 20);
                conditions.put("downloadThroughput", 4 * 1024 * 1024);
                conditions.put("uploadThroughput", 3 * 1024 * 1024);
                break;
        }
        driver.executeCdpCommand(
            "Network.emulateNetworkConditions", 
            conditions
        );
    }
}
```

## Security Testing Integration

### 1. OWASP ZAP Integration
```java
public class ZAPScanner {
    private ClientApi api;
    private String target;

    public ZAPScanner(String zapAddress, int zapPort, String target) {
        this.api = new ClientApi(zapAddress, zapPort);
        this.target = target;
    }

    public void runActiveScan() throws ClientApiException {
        // Start spidering
        api.spider.scan(target, null, null, null, null);
        
        // Wait for spider to complete
        while (Integer.parseInt(api.spider.status("")) < 100) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        // Start active scan
        api.ascan.scan(target, "True", "False", null, null, null);
        
        // Wait for scan to complete
        while (Integer.parseInt(api.ascan.status("")) < 100) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public String generateReport() throws ClientApiException {
        return new String(api.core.htmlreport());
    }
}
```

## Docker Integration

### 1. Selenium Grid with Docker
```yaml
# docker-compose.yml
version: '3'
services:
  hub:
    image: selenium/hub:latest
    ports:
      - "4444:4444"

  chrome:
    image: selenium/node-chrome:latest
    depends_on:
      - hub
    environment:
      - HUB_HOST=hub
      - HUB_PORT=4444
      - NODE_MAX_INSTANCES=5
      - NODE_MAX_SESSION=5

  firefox:
    image: selenium/node-firefox:latest
    depends_on:
      - hub
    environment:
      - HUB_HOST=hub
      - HUB_PORT=4444
      - NODE_MAX_INSTANCES=5
      - NODE_MAX_SESSION=5
```

### 2. Remote WebDriver Setup
```java
public class RemoteDriverFactory {
    public static WebDriver createDriver(String browser) 
            throws MalformedURLException {
        String hubUrl = "http://localhost:4444/wd/hub";
        
        switch (browser.toLowerCase()) {
            case "chrome":
                ChromeOptions chromeOptions = new ChromeOptions();
                return new RemoteWebDriver(
                    new URL(hubUrl), 
                    chromeOptions
                );
            
            case "firefox":
                FirefoxOptions firefoxOptions = new FirefoxOptions();
                return new RemoteWebDriver(
                    new URL(hubUrl), 
                    firefoxOptions
                );
            
            default:
                throw new IllegalArgumentException(
                    "Browser not supported: " + browser
                );
        }
    }
}
```

## Cloud Testing Integration

### 1. BrowserStack Integration
```java
public class BrowserStackConfig {
    public static WebDriver createDriver(String browser, 
                                       String version, 
                                       String os) {
        String USERNAME = System.getenv("BROWSERSTACK_USERNAME");
        String ACCESS_KEY = System.getenv("BROWSERSTACK_ACCESS_KEY");
        String URL = "https://" + USERNAME + ":" + ACCESS_KEY + 
                    "@hub-cloud.browserstack.com/wd/hub";

        DesiredCapabilities caps = new DesiredCapabilities();
        caps.setCapability("browser", browser);
        caps.setCapability("browser_version", version);
        caps.setCapability("os", os);
        caps.setCapability("name", "Test Run - " + 
            LocalDateTime.now().toString());

        try {
            return new RemoteWebDriver(new URL(URL), caps);
        } catch (MalformedURLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
```

### 2. Sauce Labs Integration
```java
public class SauceLabsConfig {
    public static WebDriver createDriver(String browser, 
                                       String version, 
                                       String platform) {
        String USERNAME = System.getenv("SAUCE_USERNAME");
        String ACCESS_KEY = System.getenv("SAUCE_ACCESS_KEY");
        String URL = "https://" + USERNAME + ":" + ACCESS_KEY + 
                    "@ondemand.saucelabs.com:443/wd/hub";

        MutableCapabilities caps = new MutableCapabilities();
        caps.setCapability("browserName", browser);
        caps.setCapability("browserVersion", version);
        caps.setCapability("platformName", platform);

        try {
            return new RemoteWebDriver(new URL(URL), caps);
        } catch (MalformedURLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
```

## Logging and Monitoring

### 1. Log4j Configuration
```java
public class LoggerConfig {
    private static Logger logger = 
        LogManager.getLogger(LoggerConfig.class);

    public static void setupLogging() {
        PropertyConfigurator.configure("log4j.properties");
    }

    public static void logStep(String step) {
        logger.info("Step: " + step);
    }

    public static void logError(String error, Exception e) {
        logger.error("Error: " + error, e);
    }
}
```

### 2. Custom Event Listener
```java
public class WebDriverEventListener 
        implements org.openqa.selenium.support.events.WebDriverEventListener {
    private static final Logger logger = 
        LogManager.getLogger(WebDriverEventListener.class);

    @Override
    public void beforeNavigateTo(String url, WebDriver driver) {
        logger.info("Navigating to: " + url);
    }

    @Override
    public void afterNavigateTo(String url, WebDriver driver) {
        logger.info("Navigated to: " + url);
    }

    @Override
    public void beforeClickOn(WebElement element, WebDriver driver) {
        logger.info("Clicking on: " + 
            element.getAttribute("outerHTML"));
    }

    // Implement other methods...
}
```

## Resources and Tools

### 1. Recommended Tools
- Selenium IDE for record and playback
- Browser Developer Tools
- Postman for API testing
- JMeter for performance testing
- OWASP ZAP for security testing

### 2. Debugging Tools
- Chrome DevTools Protocol integration
- Remote debugging
- Network traffic analysis
- Performance profiling

### 3. Learning Resources
- Online courses and certifications
- Practice websites for automation
- Community forums and discussion groups
- Automation testing blogs and newsletters

## Best Practices Checklist

### 1. Code Quality
- [ ] Use proper naming conventions
- [ ] Implement error handling
- [ ] Add comments and documentation
- [ ] Follow coding standards
- [ ] Use version control

### 2. Test Design
- [ ] Create independent tests
- [ ] Implement proper assertions
- [ ] Use test data management
- [ ] Handle timeouts properly
- [ ] Implement reporting

### 3. Framework Design
- [ ] Use Page Object Model
- [ ] Implement proper logging
- [ ] Use configuration management
- [ ] Handle different environments
- [ ] Implement CI/CD integration

## Conclusion

This comprehensive guide covers the essential aspects of Selenium WebDriver with Java, from basic setup to advanced framework design. Remember to:

1. Start with proper setup and configuration
2. Master the basics before moving to advanced concepts
3. Follow best practices and patterns
4. Continuously update and maintain your framework
5. Stay current with new features and updates

For more information and updates, visit:
- [Selenium Official Website](https://www.selenium.dev)
- [Selenium GitHub Repository](https://github.com/SeleniumHQ/selenium)
- [Selenium Documentation](https://www.selenium.dev/documentation/en/)

## Eclipse-Specific Features for Selenium

### 1. Eclipse Workspace Setup
```plaintext
workspace/
├── selenium-project/
│   ├── src/
│   │   ├── main/
│   │   │   └── java/
│   │   │       └── com/example/
│   │   │           ├── pages/
│   │   │           ├── utils/
│   │   │           └── config/
│   │   └── test/
│   │       ├── java/
│   │       │   └── com/example/
│   │       │       ├── tests/
│   │       │       └── suites/
│   │       └── resources/
│   │           ├── testdata/
│   │           ├── drivers/
│   │           └── config/
│   ├── test-output/
│   ├── screenshots/
│   └── logs/
```

### 2. Essential Eclipse Plugins
1. **TestNG for Eclipse**
   - Installation: Help > Eclipse Marketplace > Search "TestNG"
   - Features:
     - TestNG test runner
     - Test result visualization
     - XML suite editor
     - Test history

2. **Maven Integration**
   - Installation: Help > Eclipse Marketplace > Search "Maven"
   - Features:
     - POM editor
     - Dependency management
     - Project build lifecycle
     - Run configurations

3. **Cucumber Eclipse Plugin**
   - Installation: Help > Eclipse Marketplace > Search "Cucumber"
   - Features:
     - Feature file editor
     - Step definition generation
     - Gherkin syntax highlighting
     - Quick fix suggestions

### 3. Eclipse Debug Configuration
```java
// Create Debug Configuration
1. Run > Debug Configurations
2. Right-click on Java Application > New Configuration
3. Configure:
   - Project: selenium-project
   - Main class: com.example.tests.TestRunner
   - VM arguments: -ea -Dwebdriver.chrome.driver=./drivers/chromedriver
   - Environment variables:
     - SELENIUM_BROWSER=chrome
     - SELENIUM_URL=https://example.com
```

### 4. Eclipse Run Configurations
```xml
<!-- TestNG Run Configuration -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Selenium Test Suite">
    <test name="Regression Tests">
        <classes>
            <class name="com.example.tests.LoginTest"/>
            <class name="com.example.tests.DashboardTest"/>
        </classes>
    </test>
</suite>
```

### 5. Eclipse Shortcuts for Selenium Development
```plaintext
1. Code Navigation:
   - Ctrl + Shift + R: Open Resource
   - Ctrl + O: Quick Outline
   - F3: Go to Declaration
   - Alt + ←: Go Back

2. Code Generation:
   - Alt + Shift + S: Source menu
   - Ctrl + Space: Content assist
   - Ctrl + 1: Quick fix

3. Debugging:
   - F5: Step Into
   - F6: Step Over
   - F7: Step Return
   - F8: Resume
   - Ctrl + Shift + B: Toggle Breakpoint
```

## Advanced Selenium Concepts

### 1. Custom WebDriver Factory
```java
public class WebDriverFactory {
    private static final ThreadLocal<WebDriver> driverThread = 
        new ThreadLocal<>();
    
    public static WebDriver getDriver() {
        if (driverThread.get() == null) {
            WebDriver driver = createDriver();
            driverThread.set(driver);
        }
        return driverThread.get();
    }
    
    private static WebDriver createDriver() {
        String browser = System.getProperty("browser", "chrome");
        switch (browser.toLowerCase()) {
            case "chrome":
                return createChromeDriver();
            case "firefox":
                return createFirefoxDriver();
            default:
                throw new IllegalArgumentException(
                    "Browser not supported: " + browser);
        }
    }
    
    private static WebDriver createChromeDriver() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        
        // Add Chrome preferences
        Map<String, Object> prefs = new HashMap<>();
        prefs.put("download.default_directory", 
            System.getProperty("user.dir") + "/downloads");
        options.setExperimentalOption("prefs", prefs);
        
        return new ChromeDriver(options);
    }
}
```

### 2. Advanced Exception Handling
```java
public class WebElementWrapper {
    private WebDriver driver;
    private WebElement element;
    private By locator;
    
    public WebElementWrapper(WebDriver driver, By locator) {
        this.driver = driver;
        this.locator = locator;
    }
    
    public void click() {
        try {
            findElement().click();
        } catch (StaleElementReferenceException e) {
            refreshElement();
            findElement().click();
        } catch (ElementClickInterceptedException e) {
            scrollIntoView();
            findElement().click();
        }
    }
    
    private WebElement findElement() {
        if (element == null) {
            element = new WebDriverWait(driver, Duration.ofSeconds(10))
                .until(ExpectedConditions
                    .elementToBeClickable(locator));
        }
        return element;
    }
    
    private void refreshElement() {
        element = null;
        findElement();
    }
    
    private void scrollIntoView() {
        ((JavascriptExecutor) driver).executeScript(
            "arguments[0].scrollIntoView(true);", 
            findElement());
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 3. Advanced TestNG Listeners
```java
public class TestListener implements ITestListener {
    private static final Logger logger = 
        LogManager.getLogger(TestListener.class);
    
    @Override
    public void onTestStart(ITestResult result) {
        logger.info("Starting test: " + result.getName());
        // Initialize test data
        TestContext.init();
    }
    
    @Override
    public void onTestSuccess(ITestResult result) {
        logger.info("Test passed: " + result.getName());
        // Cleanup test data
        TestContext.cleanup();
    }
    
    @Override
    public void onTestFailure(ITestResult result) {
        logger.error("Test failed: " + result.getName());
        // Capture screenshot
        captureScreenshot(result);
        // Save page source
        savePageSource(result);
        // Save browser logs
        saveBrowserLogs(result);
        // Cleanup test data
        TestContext.cleanup();
    }
    
    private void captureScreenshot(ITestResult result) {
        WebDriver driver = TestContext.getDriver();
        if (driver instanceof TakesScreenshot) {
            File screenshot = ((TakesScreenshot) driver)
                .getScreenshotAs(OutputType.FILE);
            try {
                Files.copy(
                    screenshot.toPath(),
                    Paths.get("screenshots", 
                        result.getName() + ".png")
                );
            } catch (IOException e) {
                logger.error("Failed to save screenshot", e);
            }
        }
    }
}
```

### 4. Configuration Management
```java
public class ConfigurationManager {
    private static Properties properties;
    
    static {
        loadProperties();
    }
    
    private static void loadProperties() {
        properties = new Properties();
        String env = System.getProperty("env", "qa");
        try (InputStream input = ConfigurationManager.class
                .getClassLoader()
                .getResourceAsStream("config/" + env + ".properties")) {
            properties.load(input);
        } catch (IOException e) {
            throw new RuntimeException(
                "Failed to load properties file", e);
        }
    }
    
    public static String getProperty(String key) {
        String value = System.getProperty(key);
        return value != null ? value : properties.getProperty(key);
    }
    
    public static int getIntProperty(String key) {
        return Integer.parseInt(getProperty(key));
    }
    
    public static boolean getBooleanProperty(String key) {
        return Boolean.parseBoolean(getProperty(key));
    }
}
```

### 5. Test Data Management
```java
public class ExcelDataProvider {
    private XSSFWorkbook workbook;
    private XSSFSheet sheet;
    
    public ExcelDataProvider(String filePath, String sheetName) {
        try (FileInputStream fis = new FileInputStream(filePath)) {
            workbook = new XSSFWorkbook(fis);
            sheet = workbook.getSheet(sheetName);
        } catch (IOException e) {
            throw new RuntimeException(
                "Failed to load Excel file", e);
        }
    }
    
    @DataProvider(name = "testData")
    public Object[][] getTestData() {
        int rowCount = sheet.getLastRowNum();
        int colCount = sheet.getRow(0).getLastCellNum();
        
        Object[][] data = new Object[rowCount][colCount];
        
        for (int i = 1; i <= rowCount; i++) {
            XSSFRow row = sheet.getRow(i);
            for (int j = 0; j < colCount; j++) {
                XSSFCell cell = row.getCell(j);
                data[i-1][j] = getCellValue(cell);
            }
        }
        
        return data;
    }
    
    private Object getCellValue(XSSFCell cell) {
        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue();
            case NUMERIC:
                return cell.getNumericCellValue();
            case BOOLEAN:
                return cell.getBooleanCellValue();
            default:
                return null;
        }
    }
}
```

### 6. Advanced Reporting
```java
public class ExtentReportManager {
    private static ExtentReports extent;
    private static ThreadLocal<ExtentTest> test = 
        new ThreadLocal<>();
    
    public static void initReport() {
        if (extent == null) {
            extent = new ExtentReports();
            ExtentSparkReporter spark = new ExtentSparkReporter(
                "test-output/extent-report.html");
            extent.attachReporter(spark);
        }
    }
    
    public static void createTest(String testName) {
        test.set(extent.createTest(testName));
    }
    
    public static void logStep(String stepName, String details) {
        test.get().log(Status.INFO, stepName + ": " + details);
    }
    
    public static void logPass(String details) {
        test.get().log(Status.PASS, details);
    }
    
    public static void logFail(String details) {
        test.get().log(Status.FAIL, details);
    }
    
    public static void addScreenshot(String name, String path) {
        try {
            test.get().addScreenCaptureFromPath(path, name);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static void flushReport() {
        if (extent != null) {
            extent.flush();
        }
    }
}
```

## Eclipse Tips and Tricks for Selenium

### 1. Code Templates
```java
// Create custom code templates in Eclipse:
// Window > Preferences > Java > Editor > Templates

// Example: Test method template
@Test
public void test${name}() {
    // Arrange
    ${cursor}
    
    // Act
    
    // Assert
    
}

// Example: Page Object template
public class ${name}Page extends BasePage {
    // Locators
    private final By ${cursor} = By.id("");
    
    public ${name}Page(WebDriver driver) {
        super(driver);
    }
    
    // Methods
    
}
```

### 2. Project Explorer Organization
```plaintext
Working Sets:
1. Selenium Core
   - WebDriver configurations
   - Base classes
   - Utilities

2. Page Objects
   - All page classes
   - Component classes

3. Test Cases
   - Test classes
   - Test suites
   - Test data

4. Configuration
   - Properties files
   - XML configurations
   - Log configurations
```

### 3. Eclipse Memory Settings
```plaintext
Add to eclipse.ini:

-Xms1024m
-Xmx2048m
-XX:MaxPermSize=512m
-XX:+UseG1GC
-XX:+UseStringDeduplication
```

These additions provide:
1. Comprehensive Eclipse-specific features and configurations
2. Advanced Selenium concepts with practical implementations
3. Best practices for organizing Selenium projects in Eclipse
4. Performance optimization tips for Eclipse when working with Selenium
5. Advanced test management and reporting capabilities

Would you like me to add more details to any of these sections or add other topics?
