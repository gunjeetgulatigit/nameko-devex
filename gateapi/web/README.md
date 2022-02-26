# Exercise

Please follow the README-DevEnv.md setup guide for the server until the smoke tests and unit tests are completed:
[README-DevEnv.md](https://github.com/gitricko/nameko-devex/blob/master/README-DevEnv.md)

After that, get into the gateapi/web folder, i.e., 
```
cd gateapi/web
```

Then do npm install:
```
npm install
```

Once npm install was completed, you can start the app by doing:
```
npm run dev
```

After the app started, you can view the app by opening the browser and accessing this url: http://localhost:3000

Here are the 2 tasks that you should attempt to complete in the exercise:
1. For the **Property details** page, please implement and style the page according to this [Figma mocks](https://bit.ly/3pcGsLl). For the CSS part, please only utilize tailwind css to complete this page [Tailwind CSS docs](https://tailwindcss.com/docs/installation)
2. For **Page Two** page, please call the orders API as outlined in the [API Smoke Tests](https://github.com/gitricko/nameko-devex/blob/master/test/nex-smoketest.sh) and retrieve order with id 1 and display response from the API on the page.