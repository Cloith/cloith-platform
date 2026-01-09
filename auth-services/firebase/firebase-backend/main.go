package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/option"
)

func main() {
	// 1. Initial Setup & Firebase Connection
	ctx := context.Background()

	keyPath := os.Getenv("FIREBASE_KEY_PATH")
	if keyPath == "" {
		keyPath = "serviceAccountKey.json"
	}

	opt := option.WithCredentialsFile(keyPath)
	fbApp, err := firebase.NewApp(ctx, nil, opt)
	if err != nil {
		log.Fatalf("❌ Firebase Init Failed: %v", err)
	}

	// Create a Firebase Auth client once so we can reuse it
	authClient, err := fbApp.Auth(ctx)
	if err != nil {
		log.Fatalf("❌ Auth Client Failed: %v", err)
	}

	// 2. Initialize Fiber (The Express equivalent)
	app := fiber.New()

	// Add a logger so you can see requests in your Terminal/Skaffold logs
	app.Use(logger.New())

	// 3. Define Routes

	// Health check (standard in Kubernetes)
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.SendString("🚀 Firebase Brain is online!")
	})

	// Example: A route to verify a token
	app.Post("/verify", func(c *fiber.Ctx) error {
		// Just like req.body in Express
		type Request struct {
			IDToken string `json:"idToken"`
		}
		var body Request
		if err := c.BodyParser(&body); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Verify the token with Firebase
		token, err := authClient.VerifyIDToken(ctx, body.IDToken)
		if err != nil {
			return c.Status(401).JSON(fiber.Map{"error": "Unauthorized"})
		}

		return c.JSON(fiber.Map{
			"uid": token.UID,
			"message": "User verified!",
		})
	})

	// 4. Start Server
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000"
	}
	log.Fatal(app.Listen(":" + port))
}